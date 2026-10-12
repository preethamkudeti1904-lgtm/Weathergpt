import os
import re
import sys
import json
import datetime
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.core.config import settings
from app.weather.service import weather_service
from app.services.historical.disasters import historical_disaster_service
from app.services.climate.historical_year_service import historical_year_service
from app.services.safety.guidance import safety_guidance
from app.services.risk.hazard_engine import hazard_risk_engine
from app.ai.query_parser import parse_weather_query
from app.ai.website_registry import get_website_assistance
from app.ai.prompts import SYSTEM_PROMPT_TEMPLATE, LANGUAGE_NAMES
from app.schemas.chat import ChatRequest, ChatResponse, WeatherGroundedFacts
from app.models.chat import ChatSession, ChatMessage

def safe_log(msg: str) -> None:
    """Safely log debug messages to stdout with UTF-8 handling on Windows."""
    try:
        if hasattr(sys.stdout, "buffer") and sys.stdout.buffer:
            sys.stdout.buffer.write((msg + "\n").encode("utf-8", errors="replace"))
            sys.stdout.buffer.flush()
        else:
            print(msg.encode("ascii", errors="replace").decode("ascii"))
    except Exception:
        pass


def generate_conversation_title(query: str, intent: str, location_name: str) -> str:
    """Generate a clean, human-readable title from the first meaningful query."""
    loc_short = location_name.split(",")[0].strip()
    q_clean = query.strip().lower()

    if intent == "GREETING":
        return "New Conversation"
    if intent == "WEATHER_CURRENT":
        return f"{loc_short} Weather"
    if intent == "WEATHER_FORECAST":
        if "tomorrow" in q_clean or "రేపు" in q_clean or "कल" in q_clean:
            return f"Tomorrow's Rain & Forecast"
        return f"{loc_short} Forecast"
    if intent == "WEATHER_ALERT":
        return f"Disaster Alerts - {loc_short}"
    if intent == "WIND_WEATHER":
        return f"{loc_short} Wind & Flow"
    if intent == "HISTORICAL_DISASTER":
        return f"{loc_short} Disaster History"
    if intent == "DISASTER_RISK":
        return f"Safety & Threat Risk"
    if intent == "WEBSITE_HELP":
        return "Website Guidance"
    if intent == "CASUAL_CONVERSATION":
        if any(w in q_clean for w in ["eat", "ate", "food", "తిన్నా", "खाना"]):
            return "Casual Chat"
        return "Conversation"
    
    words = query.strip().split()
    if len(words) <= 4:
        return query.strip().title()
    return " ".join(words[:4]).title() + "..."

class AIService:
    def __init__(self):
        self.gemini_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.openai_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", "")

    async def _call_llm_if_available(self, system_prompt: str, user_query: str) -> Optional[str]:
        # 1. Try Gemini
        if self.gemini_key:
            try:
                from google import genai
                client = genai.Client(api_key=self.gemini_key)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"{system_prompt}\n\nUser Question: {user_query}"
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                print(f"[AIService] Gemini API error, falling back: {e}")

        # 2. Try OpenAI
        if self.openai_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_key)
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_query}
                    ],
                    max_tokens=650
                )
                if completion.choices:
                    return completion.choices[0].message.content.strip()
            except Exception as e:
                print(f"[AIService] OpenAI API error, falling back: {e}")

        return None

    # =========================================================================
    # LIVE TOOLS (Executed strictly when requires_weather_data == True)
    # =========================================================================

    async def tool_get_current_weather(self, location_name: str, lat: Optional[float], lon: Optional[float]) -> Dict[str, Any]:
        """Tool 1: Fresh observation from real weather provider."""
        try:
            current = await weather_service.get_current_weather(location_name, lat, lon)
            now_iso = datetime.datetime.utcnow().isoformat() + "Z"
            return {
                "success": True,
                "tool_name": "get_current_weather",
                "location_name": current.location_name,
                "country": getattr(current, "country", "India"),
                "state": getattr(current, "state", current.location_name.split(",")[-1].strip() if "," in current.location_name else ""),
                "district": getattr(current, "district", current.location_name.split(",")[0].strip()),
                "latitude": current.latitude,
                "longitude": current.longitude,
                "timezone": current.timezone,
                "temperature": current.temperature,
                "feels_like": current.feels_like,
                "humidity": current.humidity,
                "pressure": current.pressure,
                "wind_speed": current.wind_speed,
                "wind_direction": current.wind_direction,
                "wind_direction_cardinal": current.wind_direction_cardinal,
                "precipitation": current.precipitation,
                "visibility": current.visibility,
                "uv_index": current.uv_index,
                "weather_condition": current.condition,
                "sunrise": current.sunrise,
                "sunset": current.sunset,
                "observation_time": current.updated_at,
                "fetched_at": now_iso,
                "source": current.source
            }
        except Exception as e:
            return {
                "success": False,
                "tool_name": "get_current_weather",
                "error": f"Weather API error: {str(e)}",
                "fetched_at": datetime.datetime.utcnow().isoformat() + "Z",
                "source": "Weather Provider Service"
            }

    async def tool_get_forecast(self, location_name: str, lat: Optional[float], lon: Optional[float], days: int = 7) -> Dict[str, Any]:
        """Tool 2: Fresh hourly and daily forecast projections."""
        try:
            forecast = await weather_service.get_forecast(location_name, lat, lon, days=days)
            daily_summaries = []
            for d in forecast.daily[:days]:
                daily_summaries.append({
                    "date": d.date,
                    "day_name": d.day_name,
                    "temp_max": d.temp_max,
                    "temp_min": d.temp_min,
                    "condition": d.condition,
                    "precipitation": d.precipitation,
                    "rain_probability": d.rain_probability,
                    "wind_speed_max": d.wind_speed_max,
                    "uv_index_max": d.uv_index_max
                })

            hourly_summaries = []
            for h in forecast.hourly[:24]:
                hourly_summaries.append({
                    "time": h.time,
                    "temperature": h.temperature,
                    "condition": h.condition,
                    "rain_probability": h.rain_probability,
                    "precipitation": h.precipitation
                })

            return {
                "success": True,
                "tool_name": "get_forecast",
                "location_name": forecast.location_name,
                "timezone": forecast.timezone,
                "daily_forecast": daily_summaries,
                "hourly_next_24h": hourly_summaries,
                "fetched_at": datetime.datetime.utcnow().isoformat() + "Z",
                "source": "Open-Meteo / Numerical Weather Prediction Network"
            }
        except Exception as e:
            return {
                "success": False,
                "tool_name": "get_forecast",
                "error": f"Forecast API error: {str(e)}",
                "fetched_at": datetime.datetime.utcnow().isoformat() + "Z",
                "source": "Forecast Service"
            }

    async def tool_get_current_alerts(self, location_name: str, lat: Optional[float], lon: Optional[float]) -> Dict[str, Any]:
        """Tool 3: Fresh official warnings from SACHET / NDMA / IMD / CWC."""
        try:
            alerts = await weather_service.get_alerts(location_name, lat, lon)
            direct_list = []
            for a in alerts.direct_alerts:
                direct_list.append({
                    "alert_id": a.id,
                    "event": a.title,
                    "severity": a.severity,
                    "urgency": a.urgency,
                    "certainty": a.certainty,
                    "status": a.status,
                    "affected_area": a.location,
                    "effective": a.start_time,
                    "onset": a.start_time,
                    "expires": a.end_time,
                    "description": a.description,
                    "instruction": a.recommended_action,
                    "precautions": a.safety_precautions,
                    "source": a.source
                })

            regional_list = []
            for r in alerts.regional_alerts[:3]:
                regional_list.append({
                    "alert_id": r.id,
                    "event": r.title,
                    "severity": r.severity,
                    "affected_area": r.location,
                    "distance_km": r.distance_km,
                    "source": r.source
                })

            risk_dict = None
            if alerts.ai_risk_assessment:
                risk_dict = {
                    "risk_level": alerts.ai_risk_assessment.level,
                    "risk_score": alerts.ai_risk_assessment.score,
                    "confidence": alerts.ai_risk_assessment.confidence,
                    "reason": alerts.ai_risk_assessment.reason,
                    "expected_window": alerts.ai_risk_assessment.expected_window,
                    "disclaimer": alerts.ai_risk_assessment.disclaimer
                }

            return {
                "success": True,
                "tool_name": "get_current_alerts",
                "has_active_alerts": alerts.has_active_alerts,
                "service_status": alerts.service_status,
                "provider": alerts.provider,
                "direct_alerts": direct_list,
                "regional_alerts": regional_list,
                "ai_risk_assessment": risk_dict,
                "fetched_at": alerts.fetched_at,
                "source": alerts.provider
            }
        except Exception as e:
            return {
                "success": False,
                "tool_name": "get_current_alerts",
                "service_status": "service_temporarily_unavailable",
                "error": f"Disaster alert service temporarily unavailable: {str(e)}",
                "fetched_at": datetime.datetime.utcnow().isoformat() + "Z",
                "source": "SACHET / NDMA Warning Service"
            }

    def tool_get_historical_disasters(
        self,
        location_name: str,
        district: Optional[str],
        state: Optional[str],
        country: Optional[str],
        lat: Optional[float],
        lon: Optional[float]
    ) -> Dict[str, Any]:
        """Tool 4: Query verified historical disaster records from NDMA/IMD/CWC."""
        try:
            res = historical_disaster_service.get_historical_disasters(
                location_name=location_name,
                district=district,
                state=state,
                country=country,
                latitude=lat,
                longitude=lon,
                limit=4
            )
            return {
                "success": True,
                "tool_name": "get_historical_disasters",
                **res,
                "fetched_at": datetime.datetime.utcnow().isoformat() + "Z",
                "source": "NDMA / IMD / CWC Authoritative Historical Disaster Archive"
            }
        except Exception as e:
            return {
                "success": False,
                "tool_name": "get_historical_disasters",
                "error": str(e),
                "fetched_at": datetime.datetime.utcnow().isoformat() + "Z",
                "source": "Disaster Archive Service"
            }

    def tool_analyze_weather_risk(self, current_data: Dict[str, Any], forecast_data: Dict[str, Any], alerts_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tool 5: Deterministic hazard risk scoring engine."""
        has_direct = alerts_data.get("has_active_alerts", False) and len(alerts_data.get("direct_alerts", [])) > 0
        ai_risk = alerts_data.get("ai_risk_assessment")

        if ai_risk:
            return {
                "success": True,
                "tool_name": "analyze_weather_risk",
                "risk_level": ai_risk.get("risk_level", "LOW"),
                "risk_score": ai_risk.get("risk_score", 0),
                "confidence": ai_risk.get("confidence", "Moderate"),
                "reason": ai_risk.get("reason", "Standard meteorological baseline"),
                "expected_window": ai_risk.get("expected_window", "Next 12–24 hours"),
                "is_official_warning": has_direct,
                "disclaimer": "AI risk assessment is an analytical estimate based on numerical forecast data. It is not an official warning."
            }

        return {
            "success": True,
            "tool_name": "analyze_weather_risk",
            "risk_level": "LOW",
            "risk_score": 10,
            "confidence": "High",
            "reason": "Forecast metrics remain within safe seasonal thresholds.",
            "expected_window": "Next 24 hours",
            "is_official_warning": False,
            "disclaimer": "AI risk assessment is an analytical estimate based on numerical forecast data. It is not an official warning."
        }

    # =========================================================================
    # MULTILINGUAL DETERMINISTIC RESPONSE SYNTHESIS
    # =========================================================================

    def _generate_multilingual_response(
        self,
        intent: str,
        query: str,
        location: str,
        language: str,
        user_type: str,
        tools_data: Dict[str, Any]
    ) -> Tuple[str, Optional[str], List[str]]:
        """
        Produces fluent, human responses in the target language.
        CASUAL_CONVERSATION and GREETING NEVER output temperature or weather data.
        """
        lang = language if language in ["en", "hi", "te", "ta", "kn", "ml", "mr", "bn"] else "en"
        current = tools_data.get("current_weather", {})
        forecast = tools_data.get("forecast", {})
        alerts = tools_data.get("alerts", {})
        history = tools_data.get("history", {})
        risk = tools_data.get("risk", {})
        help_info = tools_data.get("website_help")

        city_short = location.split(",")[0].strip()

        suggestions = [
            f"What is the temperature in {city_short}?",
            f"Will it rain tomorrow in {city_short}?",
            "Any active disaster warnings?",
            "How do I use this website?"
        ]

        # ---------------------------------------------------------------------
        # 1. GREETING (CRITICAL: ZERO weather data)
        # ---------------------------------------------------------------------
        if intent == "GREETING":
            greetings = {
                "en": f"Hi! 👋 I'm WeatherGPT. How can I help you today? You can ask about current conditions, rain forecasts, official alerts, or how to use this website.",
                "te": f"నమస్కారం! 👋 నేను WeatherGPT ని. ఈరోజు నేను మీకు ఎలా సహాయపడగలను? మీరు ప్రస్తుత వాతావరణం, వర్ష సూచన, అధికారిక హెచ్చరికలు లేదా వెబ్‌సైట్ ఫీచర్ల గురించి అడగవచ్చు.",
                "hi": f"नमस्ते! 👋 मैं WeatherGPT हूँ। आज मैं आपकी क्या मदद कर सकता हूँ? आप वर्तमान मौसम, बारिश के पूर्वानुमान, आपदा चेतावनियों या वेबसाइट के उपयोग के बारे में पूछ सकते हैं।",
                "ta": f"வணக்கம்! 👋 நான் WeatherGPT. இன்று நான் உங்களுக்கு எவ்வாறு உதவ முடியும்? தற்போதைய வானிலை, மழை முன்னறிவிப்பு அல்லது அதிகாரப்பூர்வ எச்சரிக்கைகள் பற்றி நீங்கள் கேட்கலாம்.",
                "kn": f"ನಮಸ್ಕಾರ! 👋 ನಾನು WeatherGPT. ಇಂದು ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು? ಹವಾಮಾನ, ಮುನ್ಸೂಚನೆ ಅಥವಾ ಎಚ್ಚರಿಕೆಗಳ ಬಗ್ಗೆ ಕೇಳಬಹುದು.",
                "ml": f"നമസ്കാരം! 👋 ഞാൻ WeatherGPT. ഇന്ന് ഞാൻ നിങ്ങളെ എങ്ങനെ സഹായിക്കണം? കാലാവസ്ഥ, മഴ പ്രവചനം അല്ലെങ്കിൽ മുന്നറിയിപ്പുകളെക്കുറിച്ച് ചോദിക്കാം.",
                "mr": f"नमस्कार! 👋 मी WeatherGPT आहे. मी आज आपली काय मदत करू शकतो? हवामान, अंदाज किंवा अधिकृत सरकारी इशारे याबद्दल विचारू शकता.",
                "bn": f"নমস্কার! 👋 আমি WeatherGPT। আজ আমি আপনাকে কীভাবে সাহায্য করতে পারি? আবহাওয়া, বৃষ্টির পূর্বাভাস বা সরকারী সতর্কতা সম্পর্কে জিজ্ঞাসা করতে পারেন।"
            }
            return greetings.get(lang, greetings["en"]), None, [
                f"What is the temperature now?",
                "Will it rain today?",
                "Any active alerts?"
            ]

        # ---------------------------------------------------------------------
        # 2. CASUAL_CONVERSATION ("Have you ate?", "How are you?", "Thank you", etc.)
        # ---------------------------------------------------------------------
        if intent == "CASUAL_CONVERSATION":
            q_lower = query.lower()

            # "Have you eaten?" / "Have you ate?"
            if any(w in q_lower for w in ["eat", "ate", "eaten", "food", "breakfast", "lunch", "dinner", "తిన్నా", "భోజనం", "खाना", "भोजन", "சாப்பி", "ಊಟ", "ഭക്ഷണം", "जेवण", "খেয়ে"]):
                food_replies = {
                    "en": "I don't eat 😄, but I'm always energized and ready to help! Would you like to check the weather, rain forecast, or active disaster alerts?",
                    "te": "నాకు ఆహారం అవసరం లేదు 😄, కానీ మీకు సహాయం చేయడానికి నేను ఎల్లప్పుడూ సిద్ధంగా ఉన్నాను! ప్రస్తుత వాతావరణం లేదా వర్ష సూచనను తనిఖీ చేద్దామా?",
                    "hi": "मैं खाना नहीं खाता 😄, लेकिन आपकी मदद के लिए हमेशा तैयार और ऊर्जावान हूँ! क्या आप आज का मौसम या अलर्ट देखना चाहते हैं?",
                    "ta": "நான் சாப்பிடுவதில்லை 😄, ஆனால் உங்களுக்கு உதவ எப்போதும் தயாராக உள்ளேன்! தற்போதைய வானிலை அல்லது மழை முன்னறிவிப்பை சரிபார்க்க வேண்டுமா?",
                    "kn": "ನಾನು ಊಟ ಮಾಡುವುದಿಲ್ಲ 😄, ಆದರೆ ನಿಮಗೆ ಸಹಾಯ ಮಾಡಲು ಯಾವಾಗಲೂ ಸಿದ್ಧ! ಇಂದಿನ ಹವಾಮಾನ ಅಥವಾ ಮುನ್ಸೂಚನೆಯನ್ನು ಪರಿಶೀಲಿಸಬೇಕೇ?",
                    "ml": "ഞാൻ ഭക്ഷണം കഴിക്കാറില്ല 😄, പക്ഷെ നിങ്ങളെ സഹായിക്കാൻ ഞാൻ എപ്പോഴും സന്നദ്ധനാണ്! ഇന്നത്തെ കാലാവസ്ഥ പരിശോധിക്കണോ?",
                    "mr": "मी जेवत नाही 😄, पण तुम्हाला मदत करण्यासाठी नेहमी तयार आहे! आजचे हवामान किंवा अंदाज तपासायचे आहेत का?",
                    "bn": "আমি খাবার খাই না 😄, তবে আপনাকে সাহায্য করার জন্য সর্বদা প্রস্তুত! আজকের আবহাওয়া বা সতর্কতা দেখতে চান?"
                }
                return food_replies.get(lang, food_replies["en"]), None, suggestions

            # "How are you?"
            elif any(w in q_lower for w in ["how are you", "how are you doing", "how r u", "how is it going", "what's up", "whats up", "ఎలా ఉన్నావు", "బాగున్నారా", "कैसे हो", "क्या हाल है", "எப்படி இருக்கிறீர்கள்", "ಹೇಗಿದ್ದೀರಿ", "സുഖമാണോ", "कसे आहात", "কেমন আছেন"]):
                how_replies = {
                    "en": "I'm doing great! 😊 Ready to help with weather, forecasts, alerts, or this website. How can I help you today?",
                    "te": "నేను చాలా బాగున్నాను! 😊 వాతావరణం, వర్ష సూచనలు లేదా హెచ్చరికలతో సహాయపడటానికి సిద్ధంగా ఉన్నాను. ఈరోజు నేను మీకు ఎలా సహాయపడగలను?",
                    "hi": "मैं बहुत अच्छा हूँ! 😊 मौसम, पूर्वानुमान या आपदा चेतावनियों में मदद के लिए तैयार। आज मैं आपकी क्या मदद कर सकता हूँ?",
                    "ta": "நான் நலமாக இருக்கிறேன்! 😊 வானிலை மற்றும் முன்னறிவிப்புகளில் உதவ தயாராக உள்ளேன். இன்று நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?",
                    "kn": "ನಾನು ಚೆನ್ನಾಗಿದ್ದೇನೆ! 😊 ಹವಾಮಾನ ಮತ್ತು ಮುನ್ಸೂಚನೆಯಲ್ಲಿ ಸಹಾಯ ಮಾಡಲು ಸಿದ್ಧನಿದ್ದೇನೆ. ಇಂದು ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?",
                    "ml": "എനിക്ക് സുഖമാണ്! 😊 കാലാവസ്ഥയും പ്രവചനങ്ങളും നൽകാൻ ഞാൻ സന്നദ്ധനാണ്. ഇന്ന് ഞാൻ നിങ്ങളെ എങ്ങനെ സഹായിക്കണം?",
                    "mr": "मी मजेत आहे! 😊 हवामान व पावसाच्या अंदाजाबाबत मदत करण्यास तयार. आज मी आपली काय मदत करू शकतो?",
                    "bn": "আমি খুব ভালো আছি! 😊 আবহাওয়া এবং পূর্বাভাসের বিষয়ে সাহায্য করার জন্য প্রস্তুত। আজ আমি আপনাকে কীভাবে সাহায্য করতে পারি?"
                }
                return how_replies.get(lang, how_replies["en"]), None, suggestions

            # "Thank you" / "Thanks"
            elif any(w in q_lower for w in ["thank", "thanks", "ధన్యవాదాలు", "థాంక్స్", "धन्यवाद", "शुक्रिया", "நன்றி", "ಧನ್ಯವಾದಗಳು", "നന്ദി"]):
                thanks_replies = {
                    "en": "You're very welcome! 😊 Stay safe and feel free to ask whenever you need weather updates or disaster alerts.",
                    "te": "చాలా సంతోషం! 😊 సురక్షితంగా ఉండండి. వాతావరణం లేదా విపత్తు సమాచారం కోసం ఎప్పుడైనా అడగండి.",
                    "hi": "आपका बहुत-बहुत स्वागत है! 😊 सुरक्षित रहें और किसी भी मौसम या आपदा संबंधी जानकारी के लिए कभी भी पूछें।",
                    "ta": "மிக்க மகிழ்ச்சி! 😊 பாதுகாப்பாக இருங்கள். வானிலை தகவல்களுக்கு எப்போதும் கேளுங்கள்.",
                    "kn": "ತುಂಬಾ ಧನ್ಯವಾದಗಳು! 😊 ಸುರಕ್ಷಿತವಾಗಿರಿ. ಹವಾಮಾನ ಮಾಹಿತಿಗಾಗಿ ಯಾವಾಗ ಬೇಕಾದರೂ ಕೇಳಿ.",
                    "ml": "വളരെ നന്ദി! 😊 സുരക്ഷിതമായിരിക്കൂ. കാലാവസ്ഥ വിവരങ്ങൾക്കായി എപ്പോഴും ചോദിക്കാം.",
                    "mr": "आपले मनःपूर्वक स्वागत! 😊 सुरक्षित रहा आणि हवामान माहितीसाठी कधीही विचारा.",
                    "bn": "আপনাকে অনেক ধন্যবাদ! 😊 নিরাপদ থাকুন এবং আবহাওয়ার তথ্যের জন্য যেকোনো সময় জিজ্ঞাসা করুন।"
                }
                return thanks_replies.get(lang, thanks_replies["en"]), None, suggestions

            # Identity / "Who are you?"
            elif any(w in q_lower for w in ["who are you", "who made you", "are you an ai", "నువ్వు ఎవరు", "आप कौन हैं", "யார்"]):
                id_replies = {
                    "en": f"I am WeatherGPT AI, an intelligent conversational assistant developed for the India Meteorological Department (IMD) and Ministry of Earth Sciences (MoES). I'm currently monitoring {city_short}.",
                    "te": f"నేను WeatherGPT AI ని, భారత వాతావరణ విభాగం (IMD) మరియు భూ విజ్ఞాన మంత్రిత్వ శాఖ కోసం అభివృద్ధి చేయబడిన మేధోమయ వాతావరణ సహాయకుడిని. ప్రస్తుతం నేను {city_short} ను పర్యవేక్షిస్తున్నాను.",
                    "hi": f"मैं WeatherGPT AI हूँ, भारत मौसम विज्ञान विभाग (IMD) और पृथ्वी विज्ञान मंत्रालय के लिए विकसित एक संवादात्मक मौसम सहायक। वर्तमान में मैं {city_short} की निगरानी कर रहा हूँ।"
                }
                return id_replies.get(lang, id_replies["en"]), None, suggestions

            # Casual positive acknowledgements ("ok", "cool", "nice", "great", "awesome")
            else:
                ack_replies = {
                    "en": "Awesome! 👍 Let me know if you want to check the weather, rain forecast, or disaster alerts for your area.",
                    "te": "చాలా మంచిది! 👍 మీ ప్రాంత ప్రస్తుత వాతావరణం లేదా వర్ష సూచన గురించి తెలుసుకోవాలంటే అడగండి.",
                    "hi": "बहुत बढ़िया! 👍 जब भी आपको अपने क्षेत्र का मौसम, वर्षा पूर्वानुमान या अलर्ट देखना हो, मुझे बताएं।"
                }
                return ack_replies.get(lang, ack_replies["en"]), None, suggestions

        # ---------------------------------------------------------------------
        # 3. WEBSITE_HELP
        # ---------------------------------------------------------------------
        if intent == "WEBSITE_HELP":
            help_text = help_info or get_website_assistance(query, lang)
            return help_text or "You can navigate using the left sidebar to access Dashboard, Forecast, Alerts, and the Weather Map.", None, [
                "How do I use GPS?",
                "How do I change the language?",
                "Where can I see alerts?"
            ]

        # ---------------------------------------------------------------------
        # 4. GENERAL_KNOWLEDGE / HUMOR
        # ---------------------------------------------------------------------
        if intent == "GENERAL_KNOWLEDGE":
            q_lower = query.lower()
            if "joke" in q_lower or "జోక్" in q_lower or "चुटकुला" in q_lower:
                jokes = {
                    "en": "😄 Why did the cloud stay home from school?\nBecause it was feeling a little under the weather!\n\nIf you'd like, I can also check the real-time weather, forecast, or official alerts for you.",
                    "te": "😄 మేఘం ఎందుకు పాఠశాలకు వెళ్ళలేదు తెలుసా?\nఎందుకంటే దానికి 'వాతావరణం' బాగాలేదు!\n\nమీకు కావాలంటే మీ ప్రాంత ప్రస్తుత వాతావరణం లేదా హెచ్చరికలను కూడా నేను చెప్పగలను.",
                    "hi": "😄 बादल स्कूल क्यों नहीं गया?\nक्योंकि उसकी 'तबीयत' थोड़ी भारी लग रही थी!\n\nयदि आप चाहें, तो मैं आपके क्षेत्र का वर्तमान मौसम या आधिकारिक अलर्ट भी जांच सकता हूँ।"
                }
                return jokes.get(lang, jokes["en"]), None, suggestions
            elif "python" in q_lower:
                return "Python is a high-level programming language widely used in meteorology, numerical weather modeling, data analytics, and artificial intelligence.", None, suggestions
            elif "cyclone" in q_lower or "తుఫాను" in q_lower:
                return "A tropical cyclone is an intense circular storm system originating over warm tropical oceans, characterized by low atmospheric pressure, high winds exceeding 62 km/h, and torrential precipitation.", None, suggestions
            else:
                return "I am WeatherGPT, designed to assist with weather, forecasts, official disaster alerts, and website navigation. How can I assist your meteorological queries?", None, suggestions

        # ---------------------------------------------------------------------
        # 5. LANGUAGE_CHANGE
        # ---------------------------------------------------------------------
        if intent == "LANGUAGE_CHANGE":
            return "You can switch the entire interface language at any time using the Language selector dropdown in the top navigation bar.", None, suggestions

        # ---------------------------------------------------------------------
        # 6B. HISTORICAL_DISASTER
        # ---------------------------------------------------------------------
        if intent == "HISTORICAL_DISASTER":
            events = history.get("events", [])
            has_records = history.get("has_records", False)
            queried_loc = history.get("location_queried", location)

            if not has_records or not events:
                no_rec = {
                    "en": f"🏛️ Historical Disaster Records for {queried_loc}:\n\nNo major officially documented catastrophic flood, cyclone, or landslide disasters were found in the authoritative NDMA/IMD archives for this exact locality.",
                    "te": f"🏛️ {queried_loc} చారిత్రక విపత్తు రికార్డులు:\n\nఅధికారిక NDMA/IMD రికార్డుల ప్రకారం ఈ నిర్దిష్ట ప్రాంతంలో గతంలో ఎటువంటి భారీ విపత్తు రికార్డులు నమోదు కాలేదు.",
                    "hi": f"🏛️ {queried_loc} के लिए ऐतिहासिक आपदा रिकॉर्ड:\n\nआधिकारिक NDMA/IMD अभिलेखागार में इस सटीक स्थान के लिए कोई बड़ा दर्ज इतिहास नहीं मिला।"
                }
                return no_rec.get(lang, no_rec["en"]), None, suggestions

            lines = [f"🏛️ Authoritative Historical Disaster Records for {queried_loc} (Source: NDMA / IMD / CWC):\n"]
            for ev in events[:3]:
                ev_name = ev.get("event_name", "Historical Event")
                ev_year = ev.get("year", "Past")
                ev_type = ev.get("event_type", "Hazard")
                ev_sev = ev.get("severity", "Severe")
                ev_metrics = ev.get("rainfall_wind_metrics", "")
                ev_cas = ev.get("casualties", "")
                ev_desc = ev.get("description", "")
                ev_src = ev.get("source", "Official Government Archive")

                lines.append(f"• **{ev_year} - {ev_name}** ({ev_type} | Severity: {ev_sev})")
                if ev_metrics:
                    lines.append(f"  - Peak Metrics: {ev_metrics}")
                if ev_cas:
                    lines.append(f"  - Impact/Casualties: {ev_cas}")
                if ev_desc:
                    lines.append(f"  - Summary: {ev_desc}")
                lines.append(f"  - Official Source: {ev_src}\n")

            return "\n".join(lines), "Grounded in official NDMA/IMD/CWC historical memoirs.", suggestions

        # ---------------------------------------------------------------------
        # 7. WEATHER_ALERT & SMS DISASTER ALERTS
        # ---------------------------------------------------------------------
        if intent == "WEATHER_ALERT":
            # Check for user SMS disaster alert history inquiries (Section 25)
            q_lower = query.lower()
            is_sms_inquiry = any(k in q_lower for k in [
                "did i receive", "receive any alert", "receive this sms", "get this sms", "sms alert",
                "my alerts", "alert history", "received sms", "text alert", "why did i"
            ])
            
            sms_history = tools_data.get("user_sms_history")
            if is_sms_inquiry:
                if sms_history is not None and len(sms_history) > 0:
                    latest = sms_history[0]
                    history_lines = []
                    for h in sms_history[:3]:
                        history_lines.append(
                            f"• {h.get('hazard', 'Weather Warning')} ({h.get('severity', 'High')})\n"
                            f"  Sent: {h.get('sent_at', 'Recently')} | Status: {h.get('status', 'SENT')}\n"
                            f"  Source: {h.get('source', 'Official Authority')}\n"
                            f"  Message: \"{h.get('message', '')}\""
                        )
                    history_text = "\n\n".join(history_lines)
                    
                    explanation = (
                        f"📱 WEATHERGPT DISASTER SMS RECORD:\n\n"
                        f"You received an official disaster SMS alert because your verified alert location was within the designated warning area issued by {latest.get('source', 'the official authority')}.\n\n"
                        f"🚨 Warning Details:\n"
                        f"• Hazard: {latest.get('hazard', 'Severe Weather')}\n"
                        f"• Severity: {latest.get('severity', 'High')}\n"
                        f"• Issuing Source: {latest.get('source', 'SACHET / NDMA / IMD')}\n"
                        f"• Target Region: {latest.get('affected_area', location)}\n"
                        f"• Validity: Until {latest.get('expires_at', 'Specified Time')}\n\n"
                        f"📜 Recent SMS History:\n{history_text}\n\n"
                        f"You can manage your SMS preferences or change your alert location anytime in Settings."
                    )
                    return explanation, "Official disaster SMS history verified.", suggestions
                elif sms_history is not None and len(sms_history) == 0:
                    no_sms_msg = (
                        f"📱 Disaster SMS Alerts Status:\n"
                        f"You have not received any disaster SMS alerts yet for your verified location ({location}).\n\n"
                        f"When an official severe warning (such as Heavy Rain, Flood, or Cyclone) issued by SACHET/NDMA/IMD affects your coordinates, WeatherGPT will automatically deliver an SMS notification to your verified phone number."
                    )
                    return no_sms_msg, None, suggestions
                elif tools_data.get("user_id") is None:
                    guest_sms_msg = (
                        f"📱 Disaster SMS Alerts:\n"
                        f"To view your personalized SMS disaster alert history or configure location-based emergency SMS notifications, please log in to your account.\n\n"
                        f"WeatherGPT monitors official warnings from SACHET, NDMA, and IMD 24/7 and automatically alerts verified mobile numbers."
                    )
                    return guest_sms_msg, None, suggestions

            service_status = alerts.get("service_status", "service_ready")
            has_direct = alerts.get("has_active_alerts", False) and len(alerts.get("direct_alerts", [])) > 0
            direct_alert = alerts.get("direct_alerts", [{}])[0] if has_direct else None
            regional_alert = alerts.get("regional_alerts", [{}])[0] if alerts.get("regional_alerts") else None

            if service_status == "service_temporarily_unavailable":
                unavailable_msg = {
                    "en": "⚠️ Official Alert Service Status:\nThe official alert service (SACHET / NDMA) is temporarily unavailable. Please verify directly with local disaster management authorities.",
                    "te": "⚠️ అధికారిక హెచ్చరికల సేవా స్థితి:\nఅధికారిక హెచ్చరిక వ్యవస్థ (SACHET / NDMA) ప్రస్తుతం అందుబాటులో లేదు. దయచేసి స్థానిక విపత్తు నిర్వహణ అధికారుల సూచనలను గమనించండి.",
                    "hi": "⚠️ आधिकारिक अलर्ट सेवा स्थिति:\nआधिकारिक अलर्ट सेवा (SACHET / NDMA) अस्थायी रूप से अनुपलब्ध है। कृपया स्थानीय आपदा प्रबंधन प्राधिकरणों से सीधे संपर्क करें।"
                }
                return unavailable_msg.get(lang, unavailable_msg["en"]), None, suggestions

            if has_direct and direct_alert:
                precaution_lines = ""
                if direct_alert.get("precautions"):
                    precaution_lines = "\n\n🛡️ Safety Precautions (NDMA Guidelines):\n" + "\n".join(f"• {p}" for p in direct_alert["precautions"][:5])

                alert_text = (
                    f"⚠️ OFFICIAL GOVERNMENT WARNING (SACHET / NDMA)\n\n"
                    f"🔴 {direct_alert.get('event', 'Weather Warning').upper()}\n"
                    f"• Issuing Authority: {direct_alert.get('source', 'IMD / NDMA')}\n"
                    f"• Severity: {direct_alert.get('severity', 'Severe')} | Urgency: {direct_alert.get('urgency', 'Expected')}\n"
                    f"• Target Region: {direct_alert.get('affected_area', location)}\n"
                    f"• Validity Window: {direct_alert.get('effective', 'Active')} to {direct_alert.get('expires', 'Until further notice')}\n"
                    f"• Official Description: {direct_alert.get('description', '')}"
                    f"{precaution_lines}\n\n"
                    f"Source: {direct_alert.get('source', 'SACHET / NDMA')} | Verified Machine-Readable Feed"
                )
                return alert_text, "Active official disaster warning in effect.", suggestions
            else:
                regional_msg = ""
                if regional_alert:
                    regional_msg = f"\n\n📍 Nearby Regional Alert ({regional_alert.get('distance_km', 0):.0f} km away in {regional_alert.get('affected_area', 'nearby district')}):\n'{regional_alert.get('event')}' issued by {regional_alert.get('source')}."

                no_alert = {
                    "en": f"✅ Official Warning Status for {location}:\nThere are currently NO active official disaster warnings issued by SACHET, NDMA, or IMD for this location.\n\n🛡️ AI Risk Monitoring: {risk.get('risk_level', 'LOW')} (Score: {risk.get('risk_score', 0)}/100)\n• Reason: {risk.get('reason', 'Atmospheric parameters within normal bounds')}\n• Window: {risk.get('expected_window', 'Next 24 hours')}\n\n*Note: AI Risk Assessment is an analytical forecast estimate, not an official government warning.*{regional_msg}",
                    "te": f"✅ అధికారిక హెచ్చరికల సమాచారం ({location}):\nఈ ప్రాంతానికి ప్రస్తుతం SACHET లేదా IMD నుండి ఎటువంటి అధికారిక విపత్తు హెచ్చరికలు లేవు.\n\n🛡️ AI ముప్పు పర్యవేక్షణ: {risk.get('risk_level', 'LOW')} (రిస్క్ స్కోరు: {risk.get('risk_score', 0)}/100)\n• కారణం: {risk.get('reason', 'వాతావరణ పరిస్థితులు సాధారణ పరిమితుల్లో ఉన్నాయి')}\n• అంచనా సమయం: {risk.get('expected_window', 'తదుపరి 24 గంటలు')}\n\n*(గమనిక: ఇది కేవలం విశ్లేషణాత్మక అంచనా, అధికారిక ప్రభుత్వ హెచ్చరిక కాదు.)*{regional_msg}",
                    "hi": f"✅ आधिकारिक चेतावनी स्थिति ({location}):\nइस स्थान के लिए SACHET या IMD द्वारा वर्तमान में कोई आधिकारिक आपदा चेतावनी जारी नहीं की गई है।\n\n🛡️ AI मौसम जोखिम निगरानी: {risk.get('risk_level', 'LOW')} (स्कोर: {risk.get('risk_score', 0)}/100)\n• कारण: {risk.get('reason', 'मौसमी मानक सामान्य सीमा में हैं')}\n• समय: {risk.get('expected_window', 'अगले 24 घंटे')}\n\n*(नोट: यह एक विश्लेषणात्मक पूर्वानुमान है, आधिकारिक सरकारी चेतावनी नहीं।)*{regional_msg}"
                }
                return no_alert.get(lang, no_alert["en"]), None, suggestions

        # ---------------------------------------------------------------------
        # 8. DISASTER_RISK / DANGER CHECK
        # ---------------------------------------------------------------------
        if intent == "DISASTER_RISK":
            r_level = risk.get("risk_level", "LOW")
            r_score = risk.get("risk_score", 0)
            r_reason = risk.get("reason", "Conditions within seasonal norms")
            r_window = risk.get("expected_window", "Next 12–24 hours")
            has_direct = alerts.get("has_active_alerts", False) and len(alerts.get("direct_alerts", [])) > 0
            direct_alert = alerts.get("direct_alerts", [{}])[0] if has_direct else None

            danger_texts = {
                "en": (
                    f"🛡️ Safety & Threat Assessment for {location}:\n\n"
                    f"• Official Status: {has_direct and '⚠️ OFFICIAL WARNING ACTIVE (' + direct_alert.get('event', '') + ')' or '✅ No Active Official Warning'}\n"
                    f"• AI Threat Level: {r_level} (Risk Score: {r_score}/100)\n"
                    f"• Current Conditions: {current.get('temperature', 'N/A')}°C, {current.get('weather_condition', 'N/A')}, Wind: {current.get('wind_speed', 'N/A')} km/h, Rain: {current.get('precipitation', 0)} mm\n"
                    f"• Risk Window: {r_window}\n"
                    f"• Analysis: {r_reason}\n\n"
                    f"Travel Guidance: {'Exercise extreme caution or postpone non-essential outdoor travel.' if (r_level in ['HIGH', 'VERY HIGH', 'EXTREME'] or has_direct) else 'Outdoor conditions and routine travel are generally safe at this time.'}\n\n"
                    f"*Source: IMD/SACHET Official Warnings & Deterministic Hazard Engine*"
                ),
                "te": (
                    f"🛡️ భద్రతా & ముప్పు విశ్లేషణ ({location}):\n\n"
                    f"• అధికారిక స్థితి: {has_direct and '⚠️ అధికారిక హెచ్చరిక అమల్లో ఉంది (' + direct_alert.get('event', '') + ')' or '✅ ఎటువంటి అధికారిక హెచ్చరికలు లేవు'}\n"
                    f"• AI ముప్పు స్థాయి: {r_level} (రిస్క్ స్కోరు: {r_score}/100)\n"
                    f"• ప్రస్తుత వాతావరణం: {current.get('temperature', 'N/A')}°C, {current.get('weather_condition', 'N/A')}, గాలి వేగం: {current.get('wind_speed', 'N/A')} కి.మీ/గం\n"
                    f"• అంచనా సమయం: {r_window}\n"
                    f"• కారణం: {r_reason}\n\n"
                    f"ప్రయాణ సలహా: {'ప్రస్తుత పరిస్థితుల్లో ప్రయాణాలలో అత్యంత జాగ్రత్త వహించాలి.' if (r_level in ['HIGH', 'VERY HIGH', 'EXTREME'] or has_direct) else 'ప్రస్తుతానికి సాధారణ ప్రయాణాలు మరియు పనులకు వాతావరణం అనుకూలంగా ఉంది.'}"
                ),
                "hi": (
                    f"🛡️ सुरक्षा एवं जोखिम मूल्यांकन ({location}):\n\n"
                    f"• आधिकारिक स्थिति: {has_direct and '⚠️ आधिकारिक चेतावनी सक्रिय (' + direct_alert.get('event', '') + ')' or '✅ कोई आधिकारिक चेतावनी नहीं'}\n"
                    f"• AI जोखिम स्तर: {r_level} (जोखिम स्कोर: {r_score}/100)\n"
                    f"• वर्तमान स्थिति: {current.get('temperature', 'N/A')}°C, {current.get('weather_condition', 'N/A')}, हवा: {current.get('wind_speed', 'N/A')} किमी/घंटा\n"
                    f"• अनुमानित अवधि: {r_window}\n"
                    f"• विश्लेषण: {r_reason}\n\n"
                    f"यात्रा मार्गदर्शन: {'कठिन मौसम के कारण अनावश्यक बाहरी यात्रा से बचें।' if (r_level in ['HIGH', 'VERY HIGH', 'EXTREME'] or has_direct) else 'वर्तमान में मौसम सामान्य यात्रा के लिए सुरक्षित है।'}"
                )
            }
            return danger_texts.get(lang, danger_texts["en"]), f"Risk Score: {r_score}/100 ({r_level})", suggestions

        # ---------------------------------------------------------------------
        # 8b. WIND_WEATHER (Wind Direction, Speed, and Gusts)
        # ---------------------------------------------------------------------
        if intent == "WIND_WEATHER":
            w_spd = current.get("wind_speed", "N/A")
            w_dir = current.get("wind_direction", "N/A")
            w_card = current.get("wind_direction_cardinal", "")
            w_gust = current.get("wind_gusts", None)
            gust_str = f" | Gusts: {w_gust} km/h" if w_gust is not None else ""

            hourly_list = forecast.get("hourly_forecast", [])
            trend_lines = []
            for h in hourly_list[:4]:
                h_time = h.get("time", "").split("T")[-1][:5] if "T" in h.get("time", "") else h.get("time", "")
                h_spd = h.get("wind_speed", "N/A")
                h_card = h.get("wind_direction_cardinal", "")
                h_dir = f"{h.get('wind_direction')}°" if h.get("wind_direction") is not None else ""
                trend_lines.append(f"• {h_time}: {h_spd} km/h {h_card} ({h_dir})")
            
            trend_block = "\n" + "\n".join(trend_lines) if trend_lines else ""

            wind_texts = {
                "en": (
                    f"💨 Current Wind Report for {location}:\n\n"
                    f"• Wind Speed: {w_spd} km/h{gust_str}\n"
                    f"• Wind Direction: {w_card} ({w_dir}°)\n"
                    f"• Flow: Wind is blowing from the {w_card} direction.\n"
                    f"{'• Upcoming Wind Trend:' + trend_block if trend_block else ''}\n\n"
                    f"Explore interactive wind flow and the 24-hour forecast on the **Wind Direction Map** page.\n"
                    f"*Source: Open-Meteo / WMO High-Resolution Surface Wind Analysis*"
                ),
                "te": (
                    f"💨 ప్రస్తుత గాలి సమాచారం ({location}):\n\n"
                    f"• గాలి వేగం: {w_spd} కి.మీ/గం{gust_str}\n"
                    f"• గాలి దిశ: {w_card} ({w_dir}°)\n"
                    f"• ప్రవాహం: గాలి {w_card} దిశ నుండి వీస్తుంది.\n"
                    f"{'• రాబోయే గంటల గాలి సరళి:' + trend_block if trend_block else ''}\n\n"
                    f"పూర్తి వివరాల కోసం సైడ్‌బార్‌లోని **Wind Direction Map** చూడండి.\n"
                    f"*మూలం: Open-Meteo / WMO*"
                ),
                "hi": (
                    f"💨 वर्तमान वायु रिपोर्ट ({location}):\n\n"
                    f"• हवा की गति: {w_spd} किमी/घंटा{gust_str}\n"
                    f"• हवा की दिशा: {w_card} ({w_dir}°)\n"
                    f"• बहाव: हवा {w_card} दिशा से चल रही है।\n"
                    f"{'• आगामी घंटों का रुख:' + trend_block if trend_block else ''}\n\n"
                    f"विस्तृत जानकारी के लिए साइडबार में **Wind Direction Map** देखें।\n"
                    f"*स्रोत: Open-Meteo / WMO*"
                )
            }
            return wind_texts.get(lang, wind_texts["en"]), f"Wind: {w_spd} km/h {w_card}", suggestions

        # ---------------------------------------------------------------------
        # 9. WEATHER_FORECAST
        # ---------------------------------------------------------------------
        if intent == "WEATHER_FORECAST":
            day0 = forecast.get("daily_forecast", [{}])[0] if forecast.get("daily_forecast") else {}
            day1 = forecast.get("daily_forecast", [{}, {}])[1] if len(forecast.get("daily_forecast", [])) > 1 else day0
            rain_prob_tomorrow = day1.get("rain_probability", 0)
            temp_max_tomorrow = day1.get("temp_max", "N/A")
            temp_min_tomorrow = day1.get("temp_min", "N/A")
            cond_tomorrow = day1.get("condition", "N/A")

            forecast_texts = {
                "en": f"📅 Tomorrow's Forecast for {location}:\n• Max Temp: {temp_max_tomorrow}°C | Min Temp: {temp_min_tomorrow}°C\n• Weather: {cond_tomorrow}\n• Rain Probability: {rain_prob_tomorrow}%\n• Expected Precipitation: {day1.get('precipitation', 0)} mm\n\nSource: Open-Meteo / Numerical Weather Prediction Network",
                "te": f"📅 రేపటి వాతావరణ సూచన ({location}):\n• గరిష్ట ఉష్ణోగ్రత: {temp_max_tomorrow}°C | కనిష్ట ఉష్ణోగ్రత: {temp_min_tomorrow}°C\n• వాతావరణం: '{cond_tomorrow}'\n• వర్షం పడే అవకాశం: {rain_prob_tomorrow}%\n• అంచనా వర్షపాతం: {day1.get('precipitation', 0)} మి.మీ\n\nమూలం: Open-Meteo / NWP",
                "hi": f"📅 कल का मौसम पूर्वानुमान ({location}):\n• अधिकतम तापमान: {temp_max_tomorrow}°C | न्यूनतम तापमान: {temp_min_tomorrow}°C\n• मौसम की स्थिति: '{cond_tomorrow}'\n• बारिश की संभावना: {rain_prob_tomorrow}%\n• अनुमानित वर्षा: {day1.get('precipitation', 0)} मिमी\n\nस्रोत: Open-Meteo / NWP"
            }
            return forecast_texts.get(lang, forecast_texts["en"]), None, suggestions

        # ---------------------------------------------------------------------
        # 9B. HISTORICAL_WEATHER / CLIMATE_NORMALS (Section 18 & 32)
        # ---------------------------------------------------------------------
        if intent == "HISTORICAL_WEATHER":
            clim = tools_data.get("climate", {})
            req_year = clim.get("year")

            # Check if this is a specific calendar year dataset (Requirement 14)
            if req_year:
                summ = clim.get("summary") or {}
                src = clim.get("source") or {}
                st_name = src.get("station") or location
                dist_km = src.get("distance_km")
                dist_str = f" (~{dist_km} km away)" if dist_km is not None and dist_km > 0 else ""

                mean_t = summ.get("annual_average_temperature", "N/A")
                rain_mm = summ.get("annual_rainfall", "N/A")
                high_t = summ.get("highest_temperature", "N/A")
                low_t = summ.get("lowest_temperature", "N/A")
                wettest = summ.get("wettest_month", "N/A")
                warmest = summ.get("warmest_month", "N/A")
                rain_days = summ.get("total_rainy_days", "N/A")

                climate_texts = {
                    "en": (
                        f"📊 **Historical Meteorological Observations for {location} ({req_year})**\n\n"
                        f"• **Selected Year**: {req_year}\n"
                        f"• **Annual Total Rainfall**: {rain_mm} mm (across {rain_days} rainy days ≥2.5mm)\n"
                        f"• **Annual Average Temperature**: {mean_t}°C\n"
                        f"• **Extreme Temperatures**: Peak High: {high_t}°C | Lowest: {low_t}°C\n"
                        f"• **Wettest Month**: {wettest}\n"
                        f"• **Warmest Month**: {warmest}\n"
                        f"• **Reference Station**: {st_name}{dist_str}\n\n"
                        f"🏛️ *Source: {src.get('name', 'ECMWF ERA5 / IMD Observatory Network')} (Actual {req_year} Observations)*"
                    ),
                    "te": (
                        f"📊 **{location} చారిత్రక వాతావరణ పరిశీలనలు ({req_year})**\n\n"
                        f"• **ఎంపిక చేసిన సంవత్సరం**: {req_year}\n"
                        f"• **వార్షిక మొత్తం వర్షపాతం**: {rain_mm} మి.మీ ({rain_days} వర్షపు రోజులు)\n"
                        f"• **సగటు వార్షిక ఉష్ణోగ్రత**: {mean_t}°C\n"
                        f"• **గరిష్ట ఉష్ణోగ్రత**: {high_t}°C | కనిష్ట ఉష్ణోగ్రత: {low_t}°C\n"
                        f"• **అత్యధిక వర్షపాతం గల నెల**: {wettest}\n"
                        f"• **అత్యంత వేడిగా ఉండే నెల**: {warmest}\n"
                        f"• **సూచన స్టేషన్**: {st_name}{dist_str}"
                    ),
                    "hi": (
                        f"📊 **{location} के ऐतिहासिक मौसम अवलोकन ({req_year})**\n\n"
                        f"• **चयनित वर्ष**: {req_year}\n"
                        f"• **वार्षिक कुल वर्षा**: {rain_mm} मिमी ({rain_days} वर्षा दिवस)\n"
                        f"• **औसत वार्षिक तापमान**: {mean_t}°C\n"
                        f"• **उच्चतम तापमान**: {high_t}°C | न्यूनतम तापमान: {low_t}°C\n"
                        f"• **सबसे अधिक वर्षा वाला महीना**: {wettest}\n"
                        f"• **सबसे गर्म महीना**: {warmest}\n"
                        f"• **संदर्भ केंद्र**: {st_name}{dist_str}"
                    )
                }
                return climate_texts.get(lang, climate_texts["en"]), f"Historical {req_year}: {mean_t}°C / {rain_mm}mm", [
                    f"What was the rainfall in {city_short} in {req_year - 1}?",
                    f"What was the hottest month in {req_year}?",
                    f"What is the current temperature in {city_short}?"
                ]

            # Otherwise Climatological Normal (1991–2020)
            ref = clim.get("reference_station") or {}
            src = clim.get("source_info") or clim.get("source") or {}
            ann = clim.get("annual") or {}

            st_name = ref.get("name") or clim.get("location_name") or location
            dist_km = ref.get("distance_km")
            dist_str = f" (~{dist_km} km away)" if dist_km is not None and dist_km > 0 else ""
            period = (src.get("period") if isinstance(src, dict) else None) or clim.get("period", "1991–2020")
            org = (src.get("organization") if isinstance(src, dict) else None) or "India Meteorological Department (IMD)"

            mean_t = ann.get("mean_temperature_c") or clim.get("annual_mean_temp", "N/A")
            max_t = ann.get("max_temperature_c", "N/A")
            rain_mm = ann.get("total_precipitation_mm") or clim.get("annual_total_rainfall", "N/A")
            rain_days = ann.get("rainy_days", "N/A")
            wettest = ann.get("wettest_month") or clim.get("wettest_month", "N/A")
            warmest = ann.get("warmest_month") or clim.get("warmest_month", "N/A")

            # Check if user asked for a specific calendar year per Section 18
            year_match = re.search(r"\b(19\d\d|20\d\d)\b", query)
            year_disclaimer = ""
            if year_match:
                spec_year = year_match.group(1)
                year_disclaimer = (
                    f"\n\n⚠️ *Note: You asked about {spec_year}. The figures above represent official 30-year "
                    f"Climatological Normals ({period}), not single-year observations for {spec_year}.*"
                )

            climate_texts = {
                "en": (
                    f"📊 **Official Climate Analysis for {location}**\n\n"
                    f"• **Reference Station**: {st_name}{dist_str}\n"
                    f"• **Climatological Period**: {period} Normals\n"
                    f"• **Mean Annual Temperature**: {mean_t}°C\n"
                    f"• **Warmest Month**: {warmest} (Max: {max_t}°C)\n"
                    f"• **Annual Precipitation**: {rain_mm} mm\n"
                    f"• **Wettest Month**: {wettest}\n"
                    f"• **Typical Rainy Days (≥2.5mm)**: {rain_days} days/year\n"
                    f"{year_disclaimer}\n"
                    f"🏛️ *Source: {org} (Authoritative Climatological Normals)*"
                ),
                "te": (
                    f"📊 **{location} అధికారిక శీతోష్ణస్థితి విశ్లేషణ (Climate Normals)**\n\n"
                    f"• **సూచన స్టేషన్**: {st_name}{dist_str}\n"
                    f"• **సాధారణ కాలం**: {period} క్లైమేట్ నార్మల్స్\n"
                    f"• **సగటు వార్షిక ఉష్ణోగ్రత**: {mean_t}°C\n"
                    f"• **అత్యంత వేడిగా ఉండే నెల**: {warmest}\n"
                    f"• **వార్షిక వర్షపాతం**: {rain_mm} మి.మీ\n"
                    f"• **అత్యధిక వర్షపాతం గల నెల**: {wettest}\n"
                    f"• **వర్షపు రోజులు**: ఏడాదికి {rain_days} రోజులు\n"
                    f"🏛️ *మూలం: {org}*"
                ),
                "hi": (
                    f"📊 **{location} का आधिकारिक जलवायु विश्लेषण (Climate Normals)**\n\n"
                    f"• **संदर्भ केंद्र**: {st_name}{dist_str}\n"
                    f"• **जलवायु अवधि**: {period} मानक (Normals)\n"
                    f"• **औसत वार्षिक तापमान**: {mean_t}°C\n"
                    f"• **सबसे गर्म महीना**: {warmest}\n"
                    f"• **वार्षिक वर्षा**: {rain_mm} मिमी\n"
                    f"• **सबसे अधिक वर्षा वाला महीना**: {wettest}\n"
                    f"• **औसत वर्षा दिवस**: {rain_days} दिन/वर्ष\n"
                    f"🏛️ *स्रोत: {org}*"
                )
            }
            return climate_texts.get(lang, climate_texts["en"]), f"Climate: {mean_t}°C / {rain_mm}mm ({period})", [
                f"What is the wettest month in {city_short}?",
                f"What is the annual precipitation in {city_short}?",
                f"What is the current temperature in {city_short}?"
            ]

        # ---------------------------------------------------------------------
        # 10. WEATHER_CURRENT (EXPLICIT ONLY)
        # ---------------------------------------------------------------------
        if intent == "WEATHER_CURRENT":
            if current.get("success") is False:
                err_msg = {
                    "en": f"I couldn't retrieve the latest weather data for {location} right now. Please try again shortly.",
                    "te": f"{location} కోసం తాజా వాతావరణ సమాచారాన్ని ప్రస్తుతం పొందలేకపోయాను. దయచేసి కొద్దిసేపటి తర్వాత మళ్లీ ప్రయత్నించండి.",
                    "hi": f"{location} के लिए नवीनतम मौसम डेटा अभी प्राप्त नहीं हो सका। कृपया कुछ समय बाद पुनः प्रयास करें।"
                }
                return err_msg.get(lang, err_msg["en"]), None, suggestions

            temp = current.get("temperature", "N/A")
            feels = current.get("feels_like", "N/A")
            cond = current.get("weather_condition", "N/A")
            humid = current.get("humidity", "N/A")
            wind = current.get("wind_speed", "N/A")
            obs_time = current.get("observation_time", "Latest observation")
            src = current.get("source", "Open-Meteo / WMO")

            weather_texts = {
                "en": (
                    f"🌡️ Current Weather in {location}:\n"
                    f"• Temperature: {temp}°C (Feels like: {feels}°C)\n"
                    f"• Condition: {cond}\n"
                    f"• Humidity: {humid}%\n"
                    f"• Wind: {wind} km/h ({current.get('wind_direction_cardinal', 'N/A')})\n"
                    f"• Pressure: {current.get('pressure', 'N/A')} hPa | Visibility: {current.get('visibility', 'N/A')} km\n\n"
                    f"Source: {src} | Observation Time: {obs_time}"
                ),
                "te": (
                    f"🌡️ {location} లో ప్రస్తుత వాతావరణం:\n"
                    f"• ఉష్ణోగ్రత: {temp}°C (అనుభూతి: {feels}°C)\n"
                    f"• వాతావరణ పరిస్థితి: '{cond}'\n"
                    f"• గాలి తేమ: {humid}%\n"
                    f"• గాలి వేగం: {wind} కి.మీ/గం\n"
                    f"• పీడనం: {current.get('pressure', 'N/A')} hPa | దృశ్యమానత: {current.get('visibility', 'N/A')} కి.మీ\n\n"
                    f"మూలం: {src} | సమయం: {obs_time}"
                ),
                "hi": (
                    f"🌡️ {location} में वर्तमान मौसम:\n"
                    f"• तापमान: {temp}°C (महसूस: {feels}°C)\n"
                    f"• स्थिति: '{cond}'\n"
                    f"• आर्द्रता: {humid}%\n"
                    f"• हवा की गति: {wind} किमी/घंटा\n"
                    f"• वायुदाब: {current.get('pressure', 'N/A')} hPa | दृश्यता: {current.get('visibility', 'N/A')} किमी\n\n"
                    f"स्रोत: {src} | अवलोकन समय: {obs_time}"
                ),
                "ta": f"🌡️ {location} இல் தற்போதைய வானிலை: {temp}°C (உணரப்படுவது: {feels}°C), '{cond}', ஈரப்பதம்: {humid}%, காற்றின் வேகம்: {wind} கி.மீ/மணி.",
                "kn": f"🌡️ {location} ನಲ್ಲಿ ಪ್ರಸ್ತುತ ಹವಾಮಾನ: {temp}°C (ಅನಿಸಿಕೆ: {feels}°C), '{cond}', ತೇವಾಂಶ: {humid}%, ಗಾಳಿಯ ವೇಗ: {wind} ಕಿಮೀ/ಗಂ.",
                "ml": f"🌡️ {location} ലെ നിലവിലെ കാലാവസ്ഥ: {temp}°C (അനുഭവപ്പെടുന്നത്: {feels}°C), '{cond}', ഈർപ്പം: {humid}%, കാറ്റിന്റെ വേഗത: {wind} km/h.",
                "mr": f"🌡️ {location} मधील सध्याचे हवामान: {temp}°C (अनुभव: {feels}°C), '{cond}', आर्द्रता: {humid}%, वाऱ्याचा वेग: {wind} किमी/तास.",
                "bn": f"🌡️ {location}-এ বর্তমান আবহাওয়া: {temp}°C (অনুভূত: {feels}°C), '{cond}', আর্দ্রতা: {humid}%, বাতাসের গতিবেগ: {wind} কিমি/ঘণ্টা."
            }
            return weather_texts.get(lang, weather_texts["en"]), None, suggestions

        # ---------------------------------------------------------------------
        # 11. UNCLEAR / UNSUPPORTED
        # ---------------------------------------------------------------------
        unclear_replies = {
            "en": "I didn't quite catch that. Could you clarify your question? I can assist you with current weather, forecasts, official disaster alerts, or how to use this website.",
            "te": "క్షమించండి, మీ ప్రశ్న పూర్తిగా అర్థం కాలేదు. ప్రస్తుత వాతావరణం, వర్ష సూచనలు లేదా అధికారిక విపత్తు హెచ్చరికల కోసం నన్ను అడగవచ్చు.",
            "hi": "मुझे आपकी बात पूरी तरह समझ नहीं आई। क्या आप स्पष्ट कर सकते हैं? मैं वर्तमान मौसम, पूर्वानुमान या आपदा अलर्ट में आपकी सहायता कर सकता हूँ।"
        }
        return unclear_replies.get(lang, unclear_replies["en"]), None, suggestions

    # =========================================================================
    # TWO-STAGE CHAT PROCESSING PIPELINE
    # =========================================================================

    async def process_message(self, request: ChatRequest, db: Session, user_id: Optional[int] = None) -> ChatResponse:
        """
        Two-Stage Architecture:
        STAGE 1: Intent Router (determines intent & requires_weather_data)
        STAGE 2: Tool Execution (strictly if requires_weather_data == True) & Reasoning/Synthesis
        """
        # 1. Location context resolution (Section 24: Use central location & exact coordinates)
        req_lat = request.latitude
        req_lon = request.longitude
        req_tz = request.timezone or "Asia/Kolkata"
        loc_name = request.location_name

        if request.location and isinstance(request.location, dict):
            loc_name = request.location.get("name") or request.location.get("city") or loc_name
            req_lat = request.location.get("latitude", req_lat)
            req_lon = request.location.get("longitude", req_lon)
            req_tz = request.location.get("timezone", req_tz)

        if not loc_name:
            if req_lat is not None and req_lon is not None:
                try:
                    geo = await weather_service.reverse_geocode(float(req_lat), float(req_lon))
                    loc_name = geo.get("name") or f"{float(req_lat):.4f}, {float(req_lon):.4f}"
                except Exception:
                    loc_name = f"{float(req_lat):.4f}, {float(req_lon):.4f}"
            else:
                loc_name = "Current Location"

        # 2. Conversational session context memory
        session_id = request.session_id or (int(request.conversation_id) if request.conversation_id and request.conversation_id.isdigit() else None)
        session_loc = None

        if db and session_id:
            recent_msg = db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id,
                ChatMessage.location_referenced.isnot(None)
            ).order_by(ChatMessage.timestamp.desc()).first()
            if recent_msg and recent_msg.location_referenced:
                session_loc = recent_msg.location_referenced

        # STAGE 1: Intent Classification
        parsed = parse_weather_query(request.message, loc_name, session_loc)
        intent = parsed["intent"]
        requires_weather_data = parsed["requires_weather_data"]
        tools_needed = parsed["tools_needed"]
        target_loc = parsed["target_location"]

        # Coordinates for target location
        query_lat = None if parsed["is_explicit_location"] else req_lat
        query_lon = None if parsed["is_explicit_location"] else req_lon

        # Development Debug Logging (Section 34)
        safe_log(f"[Chat Engine] USER: '{request.message}' | INTENT: {intent} | REQUIRES_WEATHER: {requires_weather_data} | TOOLS: {tools_needed} | LOCATION: {target_loc}")

        # STAGE 2: Conditional Tool Execution
        tools_data: Dict[str, Any] = {}
        tool_results_payload: List[Dict[str, Any]] = []
        sources_list: List[str] = []

        if requires_weather_data:
            # Tool: Current weather
            if "get_current_weather" in tools_needed:
                cw_res = await self.tool_get_current_weather(target_loc, query_lat, query_lon)
                tools_data["current_weather"] = cw_res
                tool_results_payload.append(cw_res)
                if cw_res.get("source"):
                    sources_list.append(cw_res["source"])

            # Tool: Forecast
            if "get_forecast" in tools_needed:
                fc_res = await self.tool_get_forecast(target_loc, query_lat, query_lon, days=7)
                tools_data["forecast"] = fc_res
                tool_results_payload.append(fc_res)
                if fc_res.get("source"):
                    sources_list.append(fc_res["source"])

            # Tool: Alerts
            if "get_current_alerts" in tools_needed:
                al_res = await self.tool_get_current_alerts(target_loc, query_lat, query_lon)
                tools_data["alerts"] = al_res
                tools_data["user_id"] = user_id
                tool_results_payload.append(al_res)
                if al_res.get("provider"):
                    sources_list.append(al_res["provider"])

                # Retrieve user's SMS disaster delivery history if logged in
                if db and user_id:
                    try:
                        from app.models.sms_alert import UserAlertSmsDelivery
                        from app.models.personalized_alert import OfficialAlert
                        user_deliveries = db.query(UserAlertSmsDelivery).filter(
                            UserAlertSmsDelivery.user_id == user_id
                        ).order_by(UserAlertSmsDelivery.sent_at.desc()).limit(5).all()

                        history_list = []
                        for d in user_deliveries:
                            off_alert = db.query(OfficialAlert).filter(OfficialAlert.id == d.alert_id).first()
                            history_list.append({
                                "alert_id": d.alert_id,
                                "phone": d.phone_number,
                                "sent_at": d.sent_at.strftime("%d %b %Y, %I:%M %p") if d.sent_at else "Recently",
                                "status": d.status,
                                "message": d.message,
                                "hazard": off_alert.hazard_type if off_alert else "Severe Weather",
                                "severity": off_alert.severity if off_alert else "High",
                                "source": off_alert.source if off_alert else "Official Source",
                                "affected_area": off_alert.affected_area if off_alert else target_loc,
                                "expires_at": off_alert.expires_at.strftime("%I:%M %p") if (off_alert and off_alert.expires_at) else "Until Notice"
                            })
                        tools_data["user_sms_history"] = history_list
                    except Exception as he:
                        safe_log(f"[Chat Engine] Error fetching user SMS history: {he}")

            # Tool: Historical disasters
            if "get_historical_disasters" in tools_needed:
                hd_res = self.tool_get_historical_disasters(
                    location_name=target_loc,
                    district=None,
                    state=None,
                    country="India",
                    lat=query_lat,
                    lon=query_lon
                )
                tools_data["history"] = hd_res
                tool_results_payload.append(hd_res)
                if hd_res.get("source"):
                    sources_list.append(hd_res["source"])

            # Tool: Risk analysis
            if "analyze_weather_risk" in tools_needed:
                rk_res = self.tool_analyze_weather_risk(
                    current_data=tools_data.get("current_weather", {}),
                    forecast_data=tools_data.get("forecast", {}),
                    alerts_data=tools_data.get("alerts", {})
                )
                tools_data["risk"] = rk_res
                tool_results_payload.append(rk_res)

            # Tool: Climate statistics (Section 32 & Location+Year)
            if "get_climate_statistics" in tools_needed:
                try:
                    target_year = parsed.get("target_year")
                    if target_year:
                        lat_r, lon_r, loc_disp = await weather_service.resolve_coordinates(target_loc, query_lat, query_lon)
                        clim_dict = await historical_year_service.get_year_data(lat_r, lon_r, loc_disp, target_year)
                        tools_data["climate"] = clim_dict
                        tool_results_payload.append({"tool_name": "get_climate_statistics", "result": clim_dict})
                        sources_list.append(clim_dict.get("source", {}).get("name", "ECMWF ERA5 / IMD Observatory Network"))
                    else:
                        clim_res = await weather_service.get_historical_climate(target_loc, query_lat, query_lon)
                        tools_data["climate"] = clim_res.model_dump() if hasattr(clim_res, "model_dump") else clim_res.dict()
                        tool_results_payload.append({"tool_name": "get_climate_statistics", "result": tools_data["climate"]})
                        if clim_res.source:
                            src_str = clim_res.source.organization if hasattr(clim_res.source, "organization") else str(clim_res.source)
                            sources_list.append(src_str)
                except Exception as ce:
                    safe_log(f"[Chat Engine] Climate stats error: {ce}")

        # Website help (independent of weather data)
        if "get_website_assistance" in tools_needed:
            wa_res = get_website_assistance(request.message, request.language or "en")
            tools_data["website_help"] = wa_res
            tool_results_payload.append({"tool_name": "get_website_assistance", "result": wa_res})

        user_lang = request.language or "en"
        lang_name = LANGUAGE_NAMES.get(user_lang, "English")
        user_type = request.user_type or "General User"

        # Synthesis
        final_text = None
        advisory = None
        suggestions = []

        # If LLM API is available and tools were executed or it's a general question, call LLM
        if (self.gemini_key or self.openai_key) and (requires_weather_data or intent in ["GENERAL_KNOWLEDGE", "CASUAL_CONVERSATION"]):
            system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
                language_name=lang_name,
                language_code=user_lang,
                user_type=user_type,
                location=target_loc,
                timezone=req_tz,
                intent=intent,
                requires_weather_data=requires_weather_data,
                tools_executed=", ".join(tools_needed) if tools_needed else "None",
                tool_data_context=json.dumps(tools_data, indent=2) if tools_data else "None (Casual or General query)"
            )
            final_text = await self._call_llm_if_available(system_prompt, request.message)

        if not final_text:
            final_text, advisory, suggestions = self._generate_multilingual_response(
                intent=intent,
                query=request.message,
                location=target_loc,
                language=user_lang,
                user_type=user_type,
                tools_data=tools_data
            )

        # Build grounded facts ONLY if current weather was legitimately fetched
        facts = None
        cw = tools_data.get("current_weather", {})
        if requires_weather_data and cw.get("success"):
            facts = WeatherGroundedFacts(
                location=target_loc,
                temperature=cw.get("temperature"),
                feels_like=cw.get("feels_like"),
                condition=cw.get("weather_condition"),
                rain_probability=tools_data.get("forecast", {}).get("daily_forecast", [{}])[0].get("rain_probability", 0),
                precipitation=cw.get("precipitation"),
                wind_speed=cw.get("wind_speed"),
                humidity=cw.get("humidity"),
                pressure=cw.get("pressure"),
                visibility=cw.get("visibility"),
                uv_index=cw.get("uv_index"),
                alerts_count=len(tools_data.get("alerts", {}).get("direct_alerts", [])),
                source=cw.get("source", "Weather Provider"),
                updated_at=cw.get("observation_time", "Recent")
            )

        # 3. Database Session Persistence & Automatic Title Generation
        resolved_session_id = session_id or 1
        if db:
            try:
                chat_session = None
                if session_id and session_id > 0:
                    chat_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()

                if not chat_session:
                    gen_title = generate_conversation_title(request.message, intent, target_loc)
                    chat_session = ChatSession(
                        user_id=user_id,
                        title=gen_title,
                        language=user_lang,
                        location_name=target_loc,
                        latitude=query_lat,
                        longitude=query_lon,
                        created_at=datetime.datetime.utcnow(),
                        updated_at=datetime.datetime.utcnow()
                    )
                    db.add(chat_session)
                    db.commit()
                    db.refresh(chat_session)
                    resolved_session_id = chat_session.id
                else:
                    # Update session title if it's currently generic and user asks a meaningful query
                    if chat_session.title in ["New Conversation", "Weather Conversation", "Conversation"] and intent != "GREETING":
                        chat_session.title = generate_conversation_title(request.message, intent, target_loc)
                    chat_session.updated_at = datetime.datetime.utcnow()
                    chat_session.location_name = target_loc
                    db.commit()

                # Save user message & assistant message
                msg_user = ChatMessage(
                    session_id=resolved_session_id,
                    role="user",
                    content=request.message,
                    intent=intent,
                    location_referenced=target_loc if requires_weather_data else None,
                    timestamp=datetime.datetime.utcnow()
                )
                msg_assistant = ChatMessage(
                    session_id=resolved_session_id,
                    role="assistant",
                    content=final_text,
                    intent=intent,
                    location_referenced=target_loc if requires_weather_data else None,
                    source_attribution=", ".join(sources_list) if sources_list else "WeatherGPT Conversational Assistant",
                    raw_weather_summary=f"{cw.get('temperature', '')}°C, {cw.get('weather_condition', '')}" if cw and requires_weather_data else None,
                    timestamp=datetime.datetime.utcnow()
                )
                db.add(msg_user)
                db.add(msg_assistant)
                db.commit()
            except Exception as dbe:
                db.rollback()
                safe_log(f"[AIService] Database session error: {dbe}")

        primary_source = sources_list[0] if sources_list else "WeatherGPT Conversational Assistant"
        current_data_timestamp = cw.get("observation_time") if requires_weather_data else datetime.datetime.utcnow().strftime("%I:%M %p UTC")

        return ChatResponse(
            session_id=resolved_session_id,
            conversation_id=resolved_session_id,
            message=final_text,
            answer=final_text,
            role="assistant",
            intent=intent,
            requires_weather_data=requires_weather_data,
            language=user_lang,
            location={"name": target_loc, "latitude": query_lat, "longitude": query_lon},
            sources=sources_list,
            data_timestamp=current_data_timestamp,
            generated_at=datetime.datetime.utcnow().isoformat() + "Z",
            tool_results=tool_results_payload,
            grounded_weather=facts,
            advisory=advisory,
            source_attribution=f"Source: {primary_source}",
            updated_at=current_data_timestamp or "Just now",
            suggested_questions=suggestions
        )

ai_service = AIService()
