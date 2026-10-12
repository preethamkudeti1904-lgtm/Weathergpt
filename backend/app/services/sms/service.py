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
from app.core.phone import normalize_and_validate_phone, mask_phone_number

logger = logging.getLogger("sms_service")

class SmsService:
    def __init__(self):
        self.salt = os.getenv("OTP_SECRET_SALT", "weathergpt-secure-sms-salt-2026")
        self.sender_id = os.getenv("SMS_SENDER_ID", "WEATHR")
        self.template_id = os.getenv("SMS_TEMPLATE_ID", "")
        self.entity_id = os.getenv("SMS_ENTITY_ID", "")

    def _get_provider(self) -> Tuple[BaseSmsProvider, bool]:
        """
        Returns (provider_instance, is_real_provider).
        Determines whether real credentials are present and configured.
        """
        provider_name = os.getenv("SMS_PROVIDER", "").lower().strip()
        api_key = os.getenv("SMS_API_KEY", "").strip()

        if provider_name == "fast2sms":
            if api_key:
                return Fast2SmsProvider(api_key=api_key), True
            # Fast2SMS requested but no API key configured
            logger.warning("SMS_PROVIDER is set to fast2sms but SMS_API_KEY is not configured.")
            return simulated_sms_provider, False

        if api_key:
            # If an API key is provided, use Fast2SmsProvider
            return Fast2SmsProvider(api_key=api_key), True

        # Default to simulated provider in development
        return simulated_sms_provider, False

    def _hash_otp(self, otp: str, phone: str) -> str:
        """
        Computes HMAC-SHA256 hash of the OTP tied to the normalized phone number and secret salt.
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
        provider, _ = self._get_provider()
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
        Generates, hashes, stores, and transmits a cryptographically secure 6-digit OTP.
        - Normalizes the phone number.
        - Enforces resend cooldown (30s) and rate limits (max 5 per 5 mins).
        - Invalidates any previous unverified OTPs for the phone.
        - In production, fails if real provider is not configured or transmission fails.
        - In development, clearly flags DEVELOPMENT MODE without falsely claiming real SMS delivery.
        """
        try:
            clean_phone, _ = normalize_and_validate_phone(phone_number)
        except ValueError as ve:
            return {
                "success": False,
                "status_code": 400,
                "error": str(ve)
            }

        logger.info(f"OTP generation requested for phone: {mask_phone_number(clean_phone)}, user_id: {user_id}")

        # Check rate-limiting: max 5 requests in last 5 minutes
        five_mins_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
        recent_count = db.query(PhoneOtp).filter(
            PhoneOtp.phone_number == clean_phone,
            PhoneOtp.created_at >= five_mins_ago
        ).count()

        if recent_count >= 5:
            logger.warning(f"Rate limit exceeded for {mask_phone_number(clean_phone)}: {recent_count} requests in 5m")
            return {
                "success": False,
                "status_code": 429,
                "error": "Too many OTP requests. Please wait a few minutes before trying again."
            }

        # Check cooldown from latest OTP: 30 seconds default
        cooldown_seconds = int(os.getenv("OTP_COOLDOWN_SECONDS", "30"))
        latest = db.query(PhoneOtp).filter(
            PhoneOtp.phone_number == clean_phone
        ).order_by(PhoneOtp.created_at.desc()).first()

        if latest:
            elapsed = (datetime.datetime.utcnow() - latest.created_at).total_seconds()
            if elapsed < cooldown_seconds:
                wait_sec = int(cooldown_seconds - elapsed) + 1
                logger.warning(f"Cooldown active for {mask_phone_number(clean_phone)}. Wait {wait_sec}s.")
                return {
                    "success": False,
                    "status_code": 429,
                    "error": f"Please wait {wait_sec} seconds before requesting a new verification code."
                }

        # Invalidate previous active, unused OTPs for this phone number
        db.query(PhoneOtp).filter(
            PhoneOtp.phone_number == clean_phone,
            PhoneOtp.is_used == False,
            PhoneOtp.expires_at > datetime.datetime.utcnow()
        ).update({"expires_at": datetime.datetime.utcnow()}, synchronize_session=False)
        db.commit()

        # Generate cryptographically secure 6-digit numeric OTP (secrets module)
        raw_otp = f"{secrets.randbelow(900000) + 100000}"
        otp_hash = self._hash_otp(raw_otp, clean_phone)

        # Configurable expiration (default: 5 minutes)
        expire_minutes = int(os.getenv("OTP_EXPIRE_MINUTES", "5"))
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=expire_minutes)

        otp_record = PhoneOtp(
            phone_number=clean_phone,
            otp_hash=otp_hash,
            user_id=user_id,
            expires_at=expires_at,
            attempts=0,
            is_used=False
        )
        db.add(otp_record)
        db.commit()

        message = f"WeatherGPT verification code: {raw_otp}. Valid for {expire_minutes} minutes. Do not share this OTP with anyone."

        provider, is_real_provider = self._get_provider()
        provider_name = "fast2sms" if is_real_provider else "development/simulated"
        logger.info(f"OTP provider selected: {provider_name}")

        if is_real_provider:
            logger.info(f"SMS send attempted for phone: {mask_phone_number(clean_phone)} via {provider_name}")
            sms_res = await provider.send_sms(clean_phone, message)
            logger.info(f"SMS provider response: status={sms_res.get('status')}, id={sms_res.get('message_id')}")

            if sms_res.get("success"):
                return {
                    "success": True,
                    "status": "SENT",
                    "is_development": False,
                    "provider": sms_res.get("provider", "fast2sms"),
                    "message": f"Verification code sent via SMS to {mask_phone_number(clean_phone)}.",
                    "phone_number": clean_phone,
                    "expires_in_seconds": expire_minutes * 60
                }
            else:
                err_detail = sms_res.get("error") or "SMS provider rejected dispatch."
                logger.error(f"SMS send failed for {mask_phone_number(clean_phone)}: {err_detail}")
                return {
                    "success": False,
                    "status_code": 502,
                    "status": "FAILED",
                    "is_development": False,
                    "provider": sms_res.get("provider", "fast2sms"),
                    "error": f"SMS provider failure: {err_detail}",
                    "phone_number": clean_phone
                }
        else:
            # No real SMS credentials configured
            is_prod = os.getenv("ENVIRONMENT", "").lower() == "production"
            if is_prod:
                logger.error(f"Production SMS failure: No SMS provider credentials configured for {mask_phone_number(clean_phone)}")
                return {
                    "success": False,
                    "status_code": 503,
                    "status": "FAILED",
                    "is_development": False,
                    "error": "SMS provider is not configured in production environment.",
                    "phone_number": clean_phone
                }

            # Development Mode: Log clearly and provide dev_otp for local testing
            logger.info(f"[DEVELOPMENT ONLY] Generated test OTP for {mask_phone_number(clean_phone)}: {raw_otp}")
            # Record in simulated provider for local tracking
            await provider.send_sms(clean_phone, message)

            return {
                "success": True,
                "status": "DEVELOPMENT_MODE",
                "is_development": True,
                "provider": "development",
                "message": "DEVELOPMENT MODE: Real SMS provider credentials not configured. Generated local test code.",
                "dev_otp": raw_otp,
                "phone_number": clean_phone,
                "expires_in_seconds": expire_minutes * 60
            }

    def verify_phone_otp(
        self,
        db: Session,
        phone_number: str,
        otp_code: str,
        user_id: Optional[int] = None
    ) -> Tuple[bool, str, int, Optional[User]]:
        """
        Validates OTP code against active hash record in database.
        Returns: (success: bool, message: str, status_code: int, user: Optional[User])
        - Strictly rejects expired codes.
        - Strictly rejects already used codes.
        - Enforces max 5 retry attempts.
        - Marks is_used=True and used_at on success.
        - Updates user.phone_verified = True and phone_verified_at.
        """
        try:
            clean_phone, _ = normalize_and_validate_phone(phone_number)
        except ValueError as ve:
            return False, str(ve), 400, None

        clean_otp = (otp_code or "").strip()
        logger.info(f"OTP verification attempted for phone: {mask_phone_number(clean_phone)}")

        now = datetime.datetime.utcnow()

        # Query active, unused, unexpired OTP for this phone
        active_otp = db.query(PhoneOtp).filter(
            PhoneOtp.phone_number == clean_phone,
            PhoneOtp.is_used == False,
            PhoneOtp.expires_at >= now
        ).order_by(PhoneOtp.created_at.desc()).first()

        if not active_otp:
            # Check why it's missing to provide a clear, helpful error message
            latest_any = db.query(PhoneOtp).filter(
                PhoneOtp.phone_number == clean_phone
            ).order_by(PhoneOtp.created_at.desc()).first()

            if latest_any and latest_any.is_used:
                logger.warning(f"OTP verification rejected for {mask_phone_number(clean_phone)}: Code already used")
                return False, "This verification code has already been used. Please request a new code.", 400, None
            elif latest_any and latest_any.expires_at < now:
                logger.warning(f"OTP verification rejected for {mask_phone_number(clean_phone)}: Code expired")
                return False, "Verification code has expired. Please request a new code.", 400, None
            else:
                logger.warning(f"OTP verification rejected for {mask_phone_number(clean_phone)}: No active OTP record")
                return False, "No active verification code found for this phone number. Please request an OTP first.", 400, None

        # Check maximum retry attempts
        if active_otp.attempts >= 5:
            logger.warning(f"OTP verification rejected for {mask_phone_number(clean_phone)}: Max attempts exceeded")
            return False, "Maximum verification attempts exceeded. Please request a new verification code.", 429, None

        active_otp.attempts += 1
        db.commit()

        # Verify HMAC-SHA256 hash using constant-time comparison
        if not self._verify_hash(clean_otp, clean_phone, active_otp.otp_hash):
            remaining = 5 - active_otp.attempts
            logger.warning(f"OTP verification failed for {mask_phone_number(clean_phone)}: Incorrect code ({remaining} attempts remaining)")
            if remaining > 0:
                return False, f"Incorrect verification code. {remaining} attempt(s) remaining.", 400, None
            else:
                return False, "Incorrect verification code. Maximum attempts reached. Please request a new code.", 429, None

        # Success! Mark OTP as used
        active_otp.is_used = True
        active_otp.used_at = datetime.datetime.utcnow()

        # Update user's phone_verified status
        user = None
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = db.query(User).filter(User.phone_number == clean_phone).first()

        if user:
            user.phone_verified = True
            user.phone_verified_at = datetime.datetime.utcnow()

        db.commit()
        if user:
            db.refresh(user)

        logger.info(f"OTP verification succeeded for phone: {mask_phone_number(clean_phone)}, user_id: {user.id if user else None}")
        return True, "Phone number verified successfully!", 200, user

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
