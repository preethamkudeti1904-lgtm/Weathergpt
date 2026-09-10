from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseSmsProvider(ABC):
    @abstractmethod
    async def send_sms(
        self,
        phone_number: str,
        message: str,
        sender_id: Optional[str] = None,
        template_id: Optional[str] = None,
        entity_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sends an SMS message to a phone number.
        Returns a dict:
        {
          "success": bool,
          "provider": str,
          "message_id": Optional[str],
          "error": Optional[str],
          "status": str ("SENT", "DELIVERED", "FAILED")
        }
        """
        pass
