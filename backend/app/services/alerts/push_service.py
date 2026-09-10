import os
import json
import base64
import logging
from typing import Dict, Any, Optional, Tuple
from py_vapid import Vapid
from pywebpush import webpush, WebPushException

logger = logging.getLogger("push_service")

VAPID_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "vapid_keys.json")

class PushNotificationService:
    def __init__(self):
        self.vapid_claims = {
            "sub": "mailto:disaster-alerts@weathergpt.gov.in"
        }
        self.public_key_b64: str = ""
        self.private_key_pem: str = ""
        self._init_vapid_keys()

    def _init_vapid_keys(self):
        """
        Loads existing VAPID keys or creates and persists a new keypair.
        """
        try:
            if os.path.exists(VAPID_FILE):
                with open(VAPID_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.public_key_b64 = data.get("public_key", "")
                    self.private_key_pem = data.get("private_key", "")
                    if self.public_key_b64 and self.private_key_pem:
                        return
        except Exception as e:
            logger.warning(f"Error loading VAPID keys from file: {e}")

        # Generate new keys
        v = Vapid()
        v.generate_keys()
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
        raw_pub = v.public_key.public_bytes(
            encoding=Encoding.X962,
            format=PublicFormat.UncompressedPoint
        )
        self.public_key_b64 = base64.urlsafe_b64encode(raw_pub).decode().rstrip("=")
        self.private_key_pem = v.private_pem().decode()

        try:
            with open(VAPID_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "public_key": self.public_key_b64,
                    "private_key": self.private_key_pem
                }, f, indent=2)
            logger.info("Generated and saved new VAPID keypair")
        except Exception as e:
            logger.warning(f"Failed to persist VAPID keys: {e}")

    def get_public_key(self) -> str:
        """
        Returns URL-safe Base64 public key for browser PushManager.subscribe()
        """
        return self.public_key_b64

    def format_alert_message(
        self,
        hazard: str,
        severity: str,
        location_name: str,
        valid_until: str,
        source: str,
        language: str = "en",
        is_update: bool = False
    ) -> Tuple[str, str]:
        """
        Generates localized title and body for disaster push notification.
        Supports English, Telugu, Hindi, Tamil, Kannada, Malayalam, Marathi, Bengali.
        """
        lang = (language or "en").lower().split("-")[0]
        prefix = "🚨 Updated Disaster Alert" if is_update else "🚨 WeatherGPT Disaster Alert"

        if lang == "te":  # Telugu
            title = f"🚨 వాతావరణ హెచ్చరిక: {severity} {hazard}"
            body = (
                f"మీరు ఎంచుకున్న {location_name} ప్రాంతాన్ని ప్రభావితం చేసే అధికారిక {hazard} హెచ్చరిక ప్రస్తుతం అమల్లో ఉంది. "
                f"చెల్లుబాటు: {valid_until}. మూలం: {source}. సురక్షిత మార్గదర్శకాల కోసం WeatherGPT తెరవండి."
            )
        elif lang == "hi":  # Hindi
            title = f"🚨 मौसम आपदा चेतावनी: {severity} {hazard}"
            body = (
                f"आपके चयनित क्षेत्र ({location_name}) के लिए आधिकारिक {hazard} चेतावनी जारी की गई है। "
                f"वैधता: {valid_until} तक। स्रोत: {source}। सुरक्षा दिशानिर्देशों के लिए WeatherGPT देखें।"
            )
        elif lang == "ta":  # Tamil
            title = f"🚨 பேரிடர் எச்சரிக்கை: {severity} {hazard}"
            body = (
                f"நீங்கள் தேர்ந்தெடுத்த {location_name} பகுதிக்கு அதிகாரப்பூர்வ {hazard} எச்சரிக்கை விடுக்கப்பட்டுள்ளது. "
                f"செல்லுபடியாகும் காலம்: {valid_until}. ஆதாரம்: {source}."
            )
        elif lang == "kn":  # Kannada
            title = f"🚨 ವಿಪತ್ತು ಎಚ್ಚರಿಕೆ: {severity} {hazard}"
            body = (
                f"ನಿಮ್ಮ {location_name} ಪ್ರದೇಶಕ್ಕೆ ಅಧಿಕೃತ {hazard} ಎಚ್ಚರಿಕೆ ಜಾರಿಯಲ್ಲಿದೆ. "
                f"ಮಾನ್ಯತೆ: {valid_until}. ಮೂಲ: {source}."
            )
        elif lang == "ml":  # Malayalam
            title = f"🚨 ദുരന്ത മുന്നറിയിപ്പ്: {severity} {hazard}"
            body = (
                f"നിങ്ങൾ തിരഞ്ഞെടുത്ത {location_name} പ്രദേശത്ത് ഔദ്യോഗിക {hazard} മുന്നറിയിപ്പ് നിലവിലുണ്ട്. "
                f"സാധുത: {valid_until}. ഉറവിടം: {source}."
            )
        elif lang == "mr":  # Marathi
            title = f"🚨 हवामान इशारा: {severity} {hazard}"
            body = (
                f"आपल्या निवडलेल्या {location_name} परिसरासाठी अधिकृत {hazard} चेतावणी जारी करण्यात आली आहे. "
                f"वैधता: {valid_until}. स्रोत: {source}."
            )
        elif lang == "bn":  # Bengali
            title = f"🚨 দুর্যোগ সতর্কতা: {severity} {hazard}"
            body = (
                f"আপনার নির্বাচিত এলাকা {location_name}-এর জন্য সরকারি {hazard} সতর্কতা জারি করা হয়েছে। "
                f"মেয়াদ: {valid_until} পর্যন্ত। উৎস: {source}."
            )
        else:  # Default English
            title = f"{prefix}: {severity} {hazard}"
            body = (
                f"An official {hazard} warning currently affects your selected area ({location_name}). "
                f"Valid until {valid_until}. Source: {source}. Open WeatherGPT for safety instructions."
            )

        return title, body

    def send_push(self, subscription_info: Dict[str, Any], payload: Dict[str, Any]) -> bool:
        """
        Sends Web Push notification to a specific push subscription.
        """
        try:
            data_str = json.dumps(payload)
            webpush(
                subscription_info=subscription_info,
                data=data_str,
                vapid_private_key=self.private_key_pem,
                vapid_claims=self.vapid_claims
            )
            return True
        except WebPushException as ex:
            logger.warning(f"WebPushException sending alert: {ex}")
            # If 410 Gone or 404, subscription is invalid/unregistered
            return False
        except Exception as e:
            logger.error(f"Unexpected error in send_push: {e}")
            return False

push_service = PushNotificationService()
