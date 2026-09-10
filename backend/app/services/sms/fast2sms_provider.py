import os
import httpx
import logging
from typing import Dict, Any, Optional
from app.services.sms.base import BaseSmsProvider

logger = logging.getLogger("fast2sms_provider")

class Fast2SmsProvider(BaseSmsProvider):
    """
    India-compatible SMS provider supporting Fast2SMS API with DLT and Quick Transactional routes.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SMS_API_KEY", "")
        self.base_url = "https://www.fast2sms.com/dev/bulkV2"

    async def send_sms(
        self,
        phone_number: str,
        message: str,
        sender_id: Optional[str] = None,
        template_id: Optional[str] = None,
        entity_id: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self.api_key:
            logger.warning("Fast2SMS API key not configured, falling back to simulation.")
            return {
                "success": False,
                "provider": "fast2sms",
                "message_id": None,
                "error": "Fast2SMS API key missing in environment",
                "status": "FAILED"
            }

        # Clean phone number (strip +91, spaces)
        clean_number = phone_number.replace("+91", "").replace(" ", "").replace("-", "").strip()

        headers = {
            "authorization": self.api_key,
            "Content-Type": "application/json"
        }

        payload: Dict[str, Any] = {
            "route": "q",  # Quick Transactional Route
            "message": message,
            "language": "english",
            "flash": 0,
            "numbers": clean_number
        }

        if sender_id and template_id:
            payload["route"] = "dlt"
            payload["sender_id"] = sender_id
            payload["message_id"] = template_id
            if entity_id:
                payload["entity_id"] = entity_id

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(self.base_url, headers=headers, json=payload)
                data = res.json()

                if res.status_code == 200 and data.get("return"):
                    req_id = data.get("request_id") or str(data.get("message", [""])[0])
                    return {
                        "success": True,
                        "provider": "fast2sms",
                        "message_id": req_id,
                        "error": None,
                        "status": "SENT"
                    }
                else:
                    err_msg = data.get("message") or "Fast2SMS API returned error"
                    logger.error(f"Fast2SMS error: {err_msg}")
                    return {
                        "success": False,
                        "provider": "fast2sms",
                        "message_id": None,
                        "error": str(err_msg),
                        "status": "FAILED"
                    }
        except Exception as e:
            logger.error(f"Fast2SMS HTTP request error: {e}")
            return {
                "success": False,
                "provider": "fast2sms",
                "message_id": None,
                "error": str(e),
                "status": "FAILED"
            }
