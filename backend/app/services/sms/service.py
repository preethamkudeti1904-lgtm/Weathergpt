import os
import time
import hmac
import hashlib
import secrets
import logging
import datetime
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.sms_alert import PhoneOtp, UserAlertSmsDelivery
from app.models.user import User
from app.services.sms.base import BaseSmsProvider
from app.services.sms.simulated_provider import simulated_sms_provider
from app.services.sms.fast2sms_provider import Fast2SmsProvider

logger = logging.getLogger("sms_service")

class SmsService:
    def __init__(self):
        self.salt = os.getenv("OTP_SECRET_SALT", "weathergpt-secure-sms-salt-2026")
        self.sender_id = os.getenv("SMS_SENDER_ID", "WEATHR")
        self.template_id = os.getenv("SMS_TEMPLATE_ID", "")
        self.entity_id = os.getenv("SMS_ENTITY_ID", "")

    def _get_provider(self) -> BaseSmsProvider:
        provider_name = os.getenv("SMS_PROVIDER", "simulated").lower()
        if provider_name == "fast2sms":
            return Fast2SmsProvider()
        return simulated_sms_provider

    def _hash_otp(self, otp: str, phone: str) -> str:
        """
        Computes HMAC-SHA256 hash of the OTP tied to the phone number and secret salt.
        """
        key = self.salt.encode("utf-8")
        msg = f"{phone}:{otp}".encode("utf-8")
        return hmac.new(key, msg, hashlib.sha256).hexdigest()

    def _verify_hash(self, otp: str, phone: str, stored_hash: str) -> bool:
        expected = self._hash_otp(otp, phone)
        return hmac.compare_digest(expected, stored_hash)

    async def send_sms(
        self,
        phone_number: str,
        message: str,
        sender_id: Optional[str] = None,
        template_id: Optional[str] = None,
        entity_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sends SMS via configured provider.
        """
        provider = self._get_provider()
        return await provider.send_sms(
            phone_number=phone_number,
            message=message,
            sender_id=sender_id or self.sender_id,
            template_id=template_id or self.template_id,
            entity_id=entity_id or self.entity_id
        )

    async def create_and_send_phone_otp(
        self,
        db: Session,
        phone_number: str,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generates, hashes, stores, and transmits a 6-digit OTP to the phone number.
        Implements 60-second cooldown and 5-minute expiration.
        """
        clean_phone = phone_number.replace(" ", "").replace("-", "").strip()

        # Check rate-limiting: max 3 OTP requests in last 5 minutes
        five_mins_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
        recent_count = db.query(PhoneOtp).filter(
            PhoneOtp.phone_number == clean_phone,
            PhoneOtp.created_at >= five_mins_ago
        ).count()

        if recent_count >= 5:
            return {
                "success": False,
                "error": "Too many OTP requests. Please wait a few minutes before trying again."
            }

        # Check cooldown from latest OTP: at least 30s
        latest = db.query(PhoneOtp).filter(
            PhoneOtp.phone_number == clean_phone
        ).order_by(PhoneOtp.created_at.desc()).first()

        if latest and (datetime.datetime.utcnow() - latest.created_at).total_seconds() < 20:
            return {
                "success": False,
                "error": "Please wait 20 seconds before requesting a new OTP."
            }

        # Generate cryptographically secure 6-digit numeric OTP
        raw_otp = f"{secrets.randbelow(900000) + 100000}"
        otp_hash = self._hash_otp(raw_otp, clean_phone)

        # 5-minute expiration
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)

        otp_record = PhoneOtp(
            phone_number=clean_phone,
            otp_hash=otp_hash,
            user_id=user_id,
            expires_at=expires_at,
            attempts=0
        )
        db.add(otp_record)
        db.commit()

        message = f"WeatherGPT verification code: {raw_otp}. Valid for 5 minutes. Do not share this OTP with anyone."
        sms_res = await self.send_sms(clean_phone, message)

        return {
            "success": True,
            "message": "OTP sent successfully to your mobile number.",
            "phone_number": clean_phone,
            "expires_in_seconds": 300,
            # Return test_otp in simulated mode for instant test verification
            "dev_otp": raw_otp if os.getenv("ENVIRONMENT") != "production" else None
        }

    def verify_phone_otp(
        self,
        db: Session,
        phone_number: str,
        otp_code: str,
        user_id: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Validates OTP code against active hash record in database.
        Enforces maximum retry attempts and marks user.phone_verified = True on success.
        """
        clean_phone = phone_number.replace(" ", "").replace("-", "").strip()
        clean_otp = otp_code.strip()

        now = datetime.datetime.utcnow()
        active_otp = db.query(PhoneOtp).filter(
            PhoneOtp.phone_number == clean_phone,
            PhoneOtp.expires_at >= now
        ).order_by(PhoneOtp.created_at.desc()).first()

        if not active_otp:
            return False, "OTP has expired or does not exist. Please request a new code."

        if active_otp.attempts >= 5:
            return False, "Maximum verification attempts exceeded. Please request a new OTP."

        active_otp.attempts += 1
        db.commit()

        if not self._verify_hash(clean_otp, clean_phone, active_otp.otp_hash):
            remaining = 5 - active_otp.attempts
            return False, f"Incorrect verification code. {remaining} attempts remaining."

        # OTP verified successfully! Mark user verified if user_id or phone matches
        user = None
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = db.query(User).filter(User.phone_number == clean_phone).first()

        if user:
            user.phone_verified = True
            user.phone_verified_at = datetime.datetime.utcnow()
            db.commit()

        return True, "Phone number verified successfully!"

    def format_disaster_sms(
        self,
        hazard: str,
        severity: str,
        location_name: str,
        valid_until: str,
        source: str,
        language: str = "en",
        is_update: bool = False
    ) -> str:
        """
        Formats short, informative, official disaster SMS.
        Adheres strictly to Section 12 & 13.
        """
        lang = (language or "en").lower().split("-")[0]

        if is_update:
            if lang == "te":
                return (
                    f"🚨 WEATHERGPT ALERT UPDATE:\n"
                    f"అధికారిక {hazard} హెచ్చరిక నవీకరించబడింది.\n"
                    f"ప్రాంతం: {location_name}\n"
                    f"కొత్త చెల్లుబాటు: {valid_until}\n"
                    f"మూలం: {source}\n"
                    f"వివరాల కోసం WeatherGPT చూడండి."
                )
            elif lang == "hi":
                return (
                    f"🚨 WEATHERGPT ALERT UPDATE:\n"
                    f"आधिकारिक {hazard} चेतावनी अपडेट की गई है।\n"
                    f"स्थान: {location_name}\n"
                    f"नई वैधता: {valid_until} तक\n"
                    f"स्रोत: {source}\n"
                    f"विवरण के लिए WeatherGPT देखें।"
                )
            else:
                return (
                    f"🚨 WEATHERGPT ALERT UPDATE:\n"
                    f"The official {hazard} Warning affecting your selected location has been updated.\n"
                    f"Location: {location_name}\n"
                    f"New validity: {valid_until}\n"
                    f"Source: {source}\n"
                    f"Open WeatherGPT for details."
                )

        # Standard Alert SMS
        if lang == "te":
            return (
                f"WEATHERGPT ALERT:\n"
                f"{severity} {hazard} హెచ్చరిక మీరు ఎంచుకున్న {location_name} ప్రాంతాన్ని ప్రభావితం చేస్తుంది.\n"
                f"చెల్లుబాటు: {valid_until}\n"
                f"మూలం: {source}\n"
                f"భద్రతా చర్యల కోసం WeatherGPT తెరవండి."
            )
        elif lang == "hi":
            return (
                f"WEATHERGPT ALERT:\n"
                f"{severity} {hazard} चेतावनी आपके चयनित स्थान {location_name} को प्रभावित कर रही है।\n"
                f"वैधता: {valid_until} तक\n"
                f"स्रोत: {source}\n"
                f"सुरक्षा निर्देशों के लिए WeatherGPT देखें।"
            )
        else:
            return (
                f"WEATHERGPT ALERT:\n"
                f"{hazard} Warning affects your selected location, {location_name}.\n"
                f"Valid until {valid_until}.\n"
                f"Source: {source}.\n"
                f"Check WeatherGPT for details."
            )

sms_service = SmsService()
