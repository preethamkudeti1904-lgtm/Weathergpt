import time
import logging
from typing import Dict, Any, Optional, List
from app.services.sms.base import BaseSmsProvider

logger = logging.getLogger("simulated_sms_provider")

class SimulatedSmsProvider(BaseSmsProvider):
    """
    Development and testing SMS provider.
    Logs messages and records them in memory for test assertions without costing credits.
    """
    def __init__(self):
        self.sent_messages: List[Dict[str, Any]] = []
        self.simulate_failure: bool = False

    async def send_sms(
        self,
        phone_number: str,
        message: str,
        sender_id: Optional[str] = None,
        template_id: Optional[str] = None,
        entity_id: Optional[str] = None
    ) -> Dict[str, Any]:
        if self.simulate_failure or phone_number.endswith("000000"):
            logger.warning(f"[Simulated SMS] Deliberate failure triggered for {phone_number}")
            return {
                "success": False,
                "provider": "simulated",
                "message_id": None,
                "error": "Simulated carrier timeout / delivery failure",
                "status": "FAILED"
            }

        msg_id = f"SIM-SMS-{int(time.time() * 1000)}"
        record = {
            "message_id": msg_id,
            "phone_number": phone_number,
            "message": message,
            "sender_id": sender_id or "WEATHR",
            "template_id": template_id,
            "entity_id": entity_id,
            "timestamp": time.time(),
            "status": "SENT"
        }
        self.sent_messages.append(record)

        logger.info(
            f"📱 [DISASTER SMS SENT] To: {phone_number} | Sender: {sender_id or 'WEATHR'} | ID: {msg_id}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{message}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )

        return {
            "success": True,
            "provider": "simulated",
            "message_id": msg_id,
            "error": None,
            "status": "SENT"
        }

simulated_sms_provider = SimulatedSmsProvider()
