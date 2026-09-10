import re
from typing import Dict, Any, Tuple, Optional, List
from app.weather.service import PRESET_LOCATIONS

def parse_weather_query(
    query: str,
    current_location: str = "Guntur, Andhra Pradesh",
    session_location: Optional[str] = None
) -> Dict[str, Any]:
    q_lower = query.lower().strip()

    # 1. Explicit location extraction from preset names
    detected_loc = None
    for loc_key, (_, _, name, state) in PRESET_LOCATIONS.items():
        pattern = r"\b" + re.escape(loc_key) + r"\b"
        if re.search(pattern, q_lower):
            detected_loc = f"{name}, {state}"
            break

    # Prioritize detected location > session location > current location
    final_location = detected_loc or session_location or current_location

    # 2. Time frame extraction
    time_frame = "now"
    if any(w in q_lower for w in ["tomorrow", "రేపు", "कल", "நாளை", "ನಾಳೆ", "നാളെ", "उद्या", "আগামীকাল"]):
        time_frame = "tomorrow"
    elif any(w in q_lower for w in ["evening", "tonight", "ఈ సాయంత్రం", "ఈ రాత్రి", "आज रात", "இன்று இரவு"]):
        time_frame = "tonight"
    elif any(w in q_lower for w in ["weekend", "వారం చివర", "वीकेंड"]):
        time_frame = "weekend"
    elif any(w in q_lower for w in ["7 day", "week", "weekly", "7 రోజుల", "7 दिन", "வாராந்திர"]):
        time_frame = "weekly"
    elif any(w in q_lower for w in ["today", "ఈరోజు", "आज", "இன்று", "ಇಂದು", "ഇന്ന്"]):
        time_frame = "today"

    # 3. Comprehensive Multi-Language Intent Classifier
    intent = "CASUAL_CONVERSATION"
    requires_weather_data = False
    tools_needed: List[str] = []

    # -------------------------------------------------------------------------
    # A. GREETING
    # -------------------------------------------------------------------------
    greeting_patterns = [
        r"^(hi|hello|hey|howdy|greetings|good morning|good afternoon|good evening)\b",
        r"^(నమస్కారం|నమస్తే|హలో|హాయ్|శుభోదయం|శుభ సాయంత్రం)\b",
        r"^(नमस्ते|नमस्कार|हैलो|हाय|सुप्रभात|शुभ संध्या)\b",
        r"^(வணக்கம்|ஹலோ|ஹாய்|காலை வணக்கம்)\b",
        r"^(ನಮಸ್ಕಾರ|ಹಲೋ|ಹಾಯ್|ಶುಭೋದಯ)\b",
        r"^(നമസ്കാരം|ഹലോ|സുപ്രഭാതം)\b",
        r"^(नमस्कार|हॅलो|हाय|शुभ सकाळ)\b",
        r"^(নমস্কার|হ্যালো|হাই|সুপ্রভাত)\b"
    ]
    is_greeting = any(re.search(p, q_lower) for p in greeting_patterns) and len(query.split()) <= 4 and not any(
        w in q_lower for w in ["weather", "temperature", "rain", "alert", "forecast", "వాతావరణం", "వర్షం", "ఉష్ణోగ్రత", "मौसम", "बारिश", "तापमान"]
    )

    if is_greeting:
        return {
            "intent": "GREETING",
            "requires_weather_data": False,
            "target_location": final_location,
            "time_frame": time_frame,
            "is_explicit_location": detected_loc is not None,
            "tools_needed": [],
            "raw_query": query
        }

    # -------------------------------------------------------------------------
    # B. CASUAL_CONVERSATION ("Have you ate?", "How are you?", "Thank you", etc.)
    # -------------------------------------------------------------------------
    casual_patterns = [
        # Eating / Food inquiries
        r"\b(have you ate|have you eaten|did you eat|had food|had breakfast|had lunch|had dinner|did you have lunch|ate anything)\b",
        r"(భోజనం చేశావా|తిన్నావా|టిఫిన్ చేశావా|ఏం తిన్నావు)",
        r"(खाना खाया|खाना खा लिया|क्या तुमने खाना खाया|भोजन किया)",
        r"(சாப்பிட்டீர்களா|சாப்பாடு ஆச்சா)",
        r"(ಊಟ ಆಯ್ತಾ|ತಿಂಡಿ ಆಯ್ತಾ)",
        r"(ഭക്ഷണം കഴിച്ചോ|ഊണ് കഴിഞ്ഞോ)",
        r"(जेवलात का|जेवण झाले का)",
        r"(খেয়েছেন কি|খাবার খেয়েছেন)",

        # "How are you?" / Wellbeing
        r"\b(how are you|how are you doing|how r u|how is it going|how are things|how do you do|what's up|whats up|wassup)\b",
        r"(ఎలా ఉన్నావు|ఎలా ఉన్నారు|బాగున్నారా|కుశలమా)",
        r"(आप कैसे हैं|कैसे हो|क्या हाल है|सब ठीक है)",
        r"(நீங்கள் எப்படி இருக்கிறீர்கள்|எப்படி இருக்கீங்க)",
        r"(ನೀವು ಹೇಗಿದ್ದೀರಿ|ಹೇಗಿದ್ದೀರ)",
        r"(സുഖമാണോ|എങ്ങനെയുണ്ട്)",
        r"(तुम्ही कसे आहात|कसे आहात)",
        r"(আপনি কেমন আছেন|কেমন আছেন)",

        # Identity / Status
        r"\b(who are you|who made you|who built you|are you an ai|are you a bot|are you there|are you human|what are you doing)\b",
        r"(నువ్వు ఎవరు|నిన్ను ఎవరు తయారు చేశారు|నువ్వు రోబోవా|ఏం చేస్తున్నావు)",
        r"(आप कौन हैं|तुम्हें किसने बनाया|क्या आप एआई हैं|क्या कर रहे हो)",
        r"(நீங்கள் யார்|உங்களை உருவாக்கியது யார்)",
        r"(ನೀವು ಯಾರು|ನಿಮ್ಮನ್ನು ಯಾರು ರಚಿಸಿದರು)",
        r"(നിങ്ങൾ ആരാണ്|എന്താണ് ചെയ്യുന്നത്)",
        r"(तू कोण आहेस|काय करत आहेस)",
        r"(আপনি কে|কি করছেন)",

        # Pleasantries / Acknowledgements
        r"\b(thank you|thanks|thank you so much|thanks a lot|ok|okay|cool|nice|great|awesome|sure|understood|got it|bye|goodbye|see you|good night|nice to meet you)\b",
        r"(ధన్యవాదాలు|చాలా థాంక్స్|సరే|బాగుంది|శుభరాత్రి|మళ్లీ కలుద్దాం)",
        r"(धन्यवाद|बहुत धन्यवाद|शुक्रिया|ठीक है|अच्छा है|शुभ रात्रि|अलविदा)",
        r"(நன்றி|சரி|நன்று|வணக்கம்)",
        r"(ಧನ್ಯವಾದಗಳು|ಸರಿ|ಶುಭರಾತ್ರಿ)",
        r"(നന്ദി|ശരി|ശുഭരാത്രി)",
        r"(धन्यवाद|ठीक आहे|छान|शुभ रात्री)",
        r"(ধন্যবাদ|ঠিক আছে|শুভ রাত্রি)"
    ]

    is_casual = any(re.search(p, q_lower) for p in casual_patterns) and not any(
        w in q_lower for w in ["weather", "temperature", "rain", "alert", "forecast", "వాతావరణం", "వర్షం", "ఉష్ణోగ్రత", "హెచ్చరిక", "मौसम", "बारिश", "तापमान", "अलर्ट"]
    )

    if is_casual:
        return {
            "intent": "CASUAL_CONVERSATION",
            "requires_weather_data": False,
            "target_location": final_location,
            "time_frame": time_frame,
            "is_explicit_location": detected_loc is not None,
            "tools_needed": [],
            "raw_query": query
        }

    # -------------------------------------------------------------------------
    # C. WEBSITE_HELP
    # -------------------------------------------------------------------------
    if any(w in q_lower for w in [
        "how do i", "how to use", "how to change", "where is", "where can i", "dark mode", "light mode", "theme",
        "change language", "use gps", "how to search", "where are alerts", "how to see map", "locate me",
        "how to use this website", "website help", "help with website",
        "ఎలా ఉపయోగించాలి", "భాష ఎలా", "డార్క్ మోడ్", "మ్యాప్ ఎక్కడ", "జీపీఎస్ ఎలా", "ఈ వెబ్‌సైట్‌ను ఎలా",
        "कैसे उपयोग करें", "भाषा कैसे बदलें", "डार्क मोड", "नक्शा कहाँ है", "जीपीएस का उपयोग", "वेबसाइट का उपयोग",
        "எப்படி மாற்றுவது", "வரைபடம் எங்கே", "இருப்பிடம் எப்படி", "இணையதளத்தை எவ்வாறு"
    ]):
        return {
            "intent": "WEBSITE_HELP",
            "requires_weather_data": False,
            "target_location": final_location,
            "time_frame": time_frame,
            "is_explicit_location": detected_loc is not None,
            "tools_needed": ["get_website_assistance"],
            "raw_query": query
        }

    # -------------------------------------------------------------------------
    # D. LANGUAGE_CHANGE
    # -------------------------------------------------------------------------
    if any(w in q_lower for w in [
        "speak in telugu", "speak in hindi", "speak in tamil", "speak in english",
        "change language to", "switch language to", "తెలుగులో మాట్లాడు", "హిందీలో మాట్లాడు",
        "हिन्दी में बोलो", "अंग्रेजी में बोलो", "தமிழில் பேசு"
    ]):
        return {
            "intent": "LANGUAGE_CHANGE",
            "requires_weather_data": False,
            "target_location": final_location,
            "time_frame": time_frame,
            "is_explicit_location": detected_loc is not None,
            "tools_needed": [],
            "raw_query": query
        }

    # -------------------------------------------------------------------------
    # E. GENERAL_KNOWLEDGE / HUMOR
    # -------------------------------------------------------------------------
    if any(w in q_lower for w in [
        "tell me a joke", "tell a joke", "joke", "make me laugh", "say a joke",
        "what is python", "what is machine learning", "what causes rain", "what is humidity", "what is atmospheric pressure",
        "what is a cyclone", "what is an earthquake", "what is climate change", "explain weather",
        "జోక్ చెప్పు", "నవ్వించు", "పైథాన్ అంటే ఏమిటి", "తుఫాను అంటే ఏమిటి",
        "चुटकुला सुनाओ", "मजाक सुनाओ", "पायथन क्या है", "चक्रवात क्या है"
    ]) and not any(w in q_lower for w in ["what is the temperature", "what's the weather", "current temperature", "ఉష్ణోగ్రత ఎంత", "तापमान कितना"]):
        return {
            "intent": "GENERAL_KNOWLEDGE",
            "requires_weather_data": False,
            "target_location": final_location,
            "time_frame": time_frame,
            "is_explicit_location": detected_loc is not None,
            "tools_needed": [],
            "raw_query": query
        }

    # -------------------------------------------------------------------------
    # F. HISTORICAL_DISASTER & HISTORICAL_WEATHER
    # -------------------------------------------------------------------------
    if any(w in q_lower for w in [
        "disasters happened", "happened here before", "past flood", "past cyclone", "history", "historical",
        "has this place flooded", "has this location experienced", "experienced floods", "experienced cyclones",
        "flooded before", "flood before", "floods before", "cyclone before", "cyclones before",
        "previous extreme", "last 10 years", "worst flood", "worst cyclone", "major flood history",
        "disaster history", "flood history", "cyclone history", "past weather disasters",
        "గతంలో విపత్తులు", "గత వరదలు", "తుఫానుల చరిత్ర", "ఇంతకు ముందు వరదలు", "వరదలు వచ్చాయా", "చరిత్రలో", "విపత్తుల చరిత్ర",
        "पहले आपदा", "बाढ़ का इतिहास", "चक्रवात का इतिहास", "क्या पहले बाढ़ आई", "पहले कभी बाढ़", "आपदा इतिहास",
        "வரலாற்று பேரிடர்கள்", "முந்தைய புயல்", "முந்தைய வெள்ளம்", "பேரிடர் வரலாறு",
        "ಹಿಂದಿನ ಪ್ರವಾಹ", "ಹಿಂದಿನ ಬಿರುಗಾಳಿ", "ಇತಿಹಾಸ", "ವಿಪತ್ತು ಇತಿಹಾಸ",
        "മുൻകാല പ്രളയം", "ചരിത്രം", "ചുഴലിക്കാറ്റ്",
        "पूर्वीचे पूर", "वादळाचा इतिहास", "आपत्ती इतिहास",
        "পূর্ববর্তী বন্যা", "ঘূর্ণিঝড়ের ইতিহাস", "আগে কি বন্যা হয়েছিল"
    ]):
        return {
            "intent": "HISTORICAL_DISASTER",
            "requires_weather_data": True,
            "target_location": final_location,
            "time_frame": time_frame,
            "is_explicit_location": detected_loc is not None,
            "tools_needed": ["get_historical_disasters"],
            "raw_query": query
        }

    # -------------------------------------------------------------------------
    # G. DISASTER_RISK / DANGER CHECK
    # -------------------------------------------------------------------------
    if any(w in q_lower for w in [
        "is it safe", "is today's rain dangerous", "safe to go outside", "safe to travel", "any danger",
        "is this rain dangerous", "can i travel", "should i stay indoors", "how bad is", "severe risk",
        "threat level", "danger level", "flood danger",
        "సురక్షితమేనా", "ప్రమాదకరమా", "బయటకు వెళ్లవచ్చా", "ప్రయాణం చేయవచ్చా", "ముప్పు ఉందా", "ప్రమాదం ఉందా",
        "क्या यह सुरक्षित है", "क्या बारिश खतरनाक है", "क्या बाहर जाना सुरक्षित है", "क्या यात्रा कर सकते हैं", "क्या कोई खतरा है",
        "பாதுகாப்பானதா", "ஆபத்தானதா", "வெளியே செல்லலாமா", "பயணம் செய்யலாமா",
        "ಸುರಕ್ಷಿತವೇ", "ಅಪಾಯಕಾರಿಯೇ", "ಹೊರಗೆ ಹೋಗಬಹುದೇ",
        "സുരക്ഷിതമാണോ", "അപകടകരമാണോ", "യാത്ര ചെയ്യാമോ",
        "सुरक्षित आहे का", "धोकादायक आहे का", "बाहेर जाणे सुरक्षित आहे का",
        "নিরাপদ কি", "বৃষ্টি কি বিপজ্জনক", "বাইরে যাওয়া কি নিরাপদ"
    ]):
        return {
            "intent": "DISASTER_RISK",
            "requires_weather_data": True,
            "target_location": final_location,
            "time_frame": time_frame,
            "is_explicit_location": detected_loc is not None,
            "tools_needed": ["get_current_weather", "get_forecast", "get_current_alerts", "analyze_weather_risk"],
            "raw_query": query
        }

    # -------------------------------------------------------------------------
    # G2. CLIMATE_ANALYSIS & HISTORICAL_WEATHER (Section 32)
    # -------------------------------------------------------------------------
    if any(w in q_lower for w in [
        "wettest month", "warmest month", "hottest month", "coldest month", "driest month",
        "usually hottest", "usually warmest", "usually wettest", "usually coldest", "usually rains",
        "month is usually", "is usually hottest", "is usually warmest", "is usually wettest",
        "annual rainfall", "annual precipitation", "how much rain does this place", "how much rain does it receive",
        "how much rain does it usually", "how much rain does", "mean annual temp", "mean annual temperature",
        "average annual temperature", "climate of", "climate analysis", "climate trends", "historical climate",
        "normal temperature", "annual temperature",
        "అత్యధిక వర్షపాతం", "అత్యంత వేడిగా ఉండే నెల", "వార్షిక వర్షపాతం", "వాతావరణ తీరు",
        "सबसे अधिक बारिश", "सबसे गर्म महीना", "वार्षिक वर्षा", "जलवायु"
    ]):
        return {
            "intent": "HISTORICAL_WEATHER",
            "requires_weather_data": True,
            "target_location": final_location,
            "time_frame": time_frame,
            "is_explicit_location": detected_loc is not None,
            "tools_needed": ["get_climate_statistics"],
            "raw_query": query
        }

    # -------------------------------------------------------------------------
    # H. WEATHER_ALERT (Official Severe Weather Warnings)
    # -------------------------------------------------------------------------
    if any(w in q_lower for w in [
        "alert", "alerts", "cyclone warning", "flood warning", "storm warning", "heatwave warning",
        "emergency warning", "hazard warning", "threat warning", "disaster warning", "sachet", "ndma",
        "active alert", "any warnings", "active warnings", "weather alert", "disaster alert", "sms",
        "sms alert", "receive sms", "why did i get this sms", "did i receive any disaster alert", "text alert",
        "హెచ్చరిక", "హెచ్చరికలు", "తుఫాను హెచ్చరిక", "వరద హెచ్చరిక", "ముప్పు హెచ్చరిక", "అలర్ట్", "అలర్ట్‌లు",
        "चेतावनी", "चेतावनियां", "अलर्ट", "तूफान चेतावनी", "बाढ़ चेतावनी", "आपदा चेतावनी",
        "எச்சரிக்கை", "புயல் எச்சரிக்கை", "வெள்ள எச்சரிக்கை", "அபாய எச்சரிக்கை",
        "ಎಚ್ಚರಿಕೆ", "ಬಿರುಗಾಳಿ ಎಚ್ಚರಿಕೆ", "ಪ್ರವಾಹ ಎಚ್ಚರಿಕೆ",
        "മുന്നറിയിപ്പ്", "അപകട മുന്നറിയിപ്പ്", "പ്രളയ മുന്നറിയിപ്പ്",
        "इशारा", "वादळ इशारा", "पूर इशारा",
        "সতর্কতা", "বন্যা সতর্কতা", "ঘূর্ণিঝড় সতর্কতা"
    ]):
        return {
            "intent": "WEATHER_ALERT",
            "requires_weather_data": True,
            "target_location": final_location,
            "time_frame": time_frame,
            "is_explicit_location": detected_loc is not None,
            "tools_needed": ["get_current_alerts"],
            "raw_query": query
        }

    # -------------------------------------------------------------------------
    # H2. WIND_WEATHER (Wind Direction, Speed, and Gusts)
    # -------------------------------------------------------------------------
    if any(w in q_lower for w in [
        "wind", "wind direction", "wind speed", "wind gusts", "gusts", "how fast is the wind",
        "which direction is the wind", "direction is the wind coming from", "is the wind strong",
        "will the wind become stronger", "show me the wind direction", "wind forecast",
        "windy", "breeze", "gale", "air direction", "blow direction",
        "గాలి దిశ", "గాలి వేగం", "గాలి ఎటు వీస్తుంది", "గాలి ఎక్కువగా ఉందా", "ఈదురు గాలులు",
        "हवा की दिशा", "हवा की गति", "हवा किस दिशा से चल रही है", "क्या हवा तेज है", "झोंके",
        "காற்றின் திசை", "காற்றின் வேகம்", "காற்று வீசும் திசை",
        "ಗಾಳಿಯ ದಿಕ್ಕು", "ಗಾಳಿಯ ವೇಗ", "ಬಿರುಗಾಳಿ",
        "കാറ്റിന്റെ ദിശ", "കാറ്റിന്റെ വേഗത",
        "वाऱ्याची दिशा", "वाऱ्याचा वेग",
        "বাতাসের দিক", "বাতাসের গতিবেগ"
    ]):
        return {
            "intent": "WIND_WEATHER",
            "requires_weather_data": True,
            "target_location": final_location,
            "time_frame": time_frame,
            "is_explicit_location": detected_loc is not None,
            "tools_needed": ["get_current_weather", "get_forecast"],
            "raw_query": query
        }

    # -------------------------------------------------------------------------
    # I. WEATHER_FORECAST
    # -------------------------------------------------------------------------
    is_forecast_query = any(w in q_lower for w in [
        "tomorrow", "tonight", "this evening", "weekend", "forecast", "7 days", "next week",
        "will it rain tomorrow", "rain tomorrow", "temperature tomorrow", "weather tomorrow",
        "hourly forecast", "weekly forecast", "future weather", "when will it rain", "when will rain stop",
        "రేపు వర్షం", "రేపటి సూచన", "రేపటి వాతావరణం", "వారం రోజుల", "ఈ రాత్రి", "భవిష్యత్ వాతావరణం",
        "कल बारिश", "कल का मौसम", "पूर्वानुमान", "आगामी 7 दिन", "कल तापमान",
        "நாளை மழை", "முன்னறிவிப்பு", "அடுத்த வாரம்", "நாளை வானிலை",
        "ನಾಳೆಯ ಹವಾಮಾನ", "ಮುನ್ಸೂಚನೆ", "ನಾಳೆ ಮಳೆ",
        "നാളത്തെ കാലാവസ്ഥ", "പ്രവചനം", "നാളെ മഴ",
        "उद्याचा अंदाज", "उद्या पाऊस", "उद्याचे हवामान",
        "কালকের আবহাওয়া", "পূর্বাভাস", "কাল কি বৃষ্টি হবে"
    ]) or (time_frame in ["tomorrow", "tonight", "weekend", "weekly"] and any(
        w in q_lower for w in ["weather", "rain", "temperature", "conditions", "hot", "cold", "వాతావరణం", "వర్షం", "ఉష్ణోగ్రత", "मौसम", "बारिश"]
    ))

    if is_forecast_query:
        return {
            "intent": "WEATHER_FORECAST",
            "requires_weather_data": True,
            "target_location": final_location,
            "time_frame": time_frame,
            "is_explicit_location": detected_loc is not None,
            "tools_needed": ["get_forecast"],
            "raw_query": query
        }

    # -------------------------------------------------------------------------
    # J. WEATHER_CURRENT (MUST BE EXPLICIT)
    # -------------------------------------------------------------------------
    is_explicit_weather = any(w in q_lower for w in [
        "temperature", "how hot", "how cold", "current weather", "what's the weather", "what is the weather",
        "weather now", "weather today", "weather right now", "outside weather", "how is the weather",
        "is it raining", "will it rain today", "chance of rain", "humidity", "wind speed", "wind direction",
        "pressure", "uv index", "visibility", "sunrise", "sunset", "atmospheric", "clouds",
        "వాతావరణం", "ఉష్ణోగ్రత", "వర్షం", "తేమ", "గాలి వేగం", "సూర్యోదయం", "సూర్యాస్తమయం",
        "मौसम", "तापमान", "बारिश", "आर्द्रता", "हवा की गति", "सूर्योदय", "सूर्यास्त",
        "வானிலை", "வெப்பநிலை", "மழை", "ஈரப்பதம்", "காற்றின் வேகம்",
        "ಹವಾಮಾನ", "ತಾಪಮಾನ", "ಮಳೆ", "ತೇವಾಂಶ", "ಗಾಳಿಯ ವೇಗ",
        "കാലാവസ്ഥ", "താപനില", "മഴ", "ഈർപ്പം",
        "हवामान", "तापमान", "पाऊस", "आर्द्रता",
        "আবহাওয়া", "তাপমাত্রা", "বৃষ্টি", "বাতাসের গতি"
    ]) or (detected_loc is not None and any(w in q_lower for w in ["in", "at", "लो", "में", "இல்", "ನಲ್ಲಿ"]))

    if is_explicit_weather:
        return {
            "intent": "WEATHER_CURRENT",
            "requires_weather_data": True,
            "target_location": final_location,
            "time_frame": "now",
            "is_explicit_location": detected_loc is not None,
            "tools_needed": ["get_current_weather"],
            "raw_query": query
        }

    # -------------------------------------------------------------------------
    # K. Fallback: CASUAL_CONVERSATION / UNCLEAR (NEVER call weather APIs!)
    # -------------------------------------------------------------------------
    # Any general statement or question not explicitly asking for weather
    return {
        "intent": "CASUAL_CONVERSATION" if len(query.split()) > 1 else "UNCLEAR",
        "requires_weather_data": False,
        "target_location": final_location,
        "time_frame": time_frame,
        "is_explicit_location": detected_loc is not None,
        "tools_needed": [],
        "raw_query": query
    }
