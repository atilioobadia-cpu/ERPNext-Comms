from abc import ABC, abstractmethod


class BaseWhatsAppAdapter(ABC):
    """Abstract base for WhatsApp providers."""

    @abstractmethod
    def handle_inbound(self, webhook_data: dict) -> dict:
        """Process incoming WhatsApp message webhook. Returns parsed message data."""

    @abstractmethod
    def send_message(self, from_number: str, to_number: str, message: str, media_url: str = None) -> dict:
        """Send a WhatsApp message. Returns {"ok": True, "message_id": "..."}."""

    @abstractmethod
    def handle_status_update(self, webhook_data: dict) -> dict:
        """Process delivery/read status callback. Returns parsed status data."""

    @abstractmethod
    def send_template(self, from_number: str, to_number: str, template_name: str, variables: dict = None) -> dict:
        """Send a pre-approved WhatsApp template message."""

    def normalize_number(self, number: str) -> str:
        """Normalize phone number — strip whatsapp: prefix, ensure + prefix."""
        number = number.replace("whatsapp:", "").strip()
        if not number.startswith("+"):
            number = "+" + number
        return number


class BaseSMSAdapter(ABC):
    """Abstract base for SMS providers."""

    @abstractmethod
    def send_sms(self, from_number: str, to_number: str, message: str) -> dict:
        """Send an SMS. Returns {"ok": True, "message_id": "..."}."""

    @abstractmethod
    def handle_delivery_report(self, webhook_data: dict) -> dict:
        """Process delivery report. Returns parsed status data."""


class BaseVoiceAdapter(ABC):
    """Abstract base for voice providers."""

    @abstractmethod
    def handle_inbound(self, webhook_data: dict) -> dict:
        """Process incoming call webhook. Returns TwiML or response data."""

    @abstractmethod
    def make_outbound(self, from_number: str, to_number: str, callback_url: str) -> dict:
        """Initiate outbound call."""

    @abstractmethod
    def handle_status_update(self, webhook_data: dict) -> dict:
        """Process call status change."""

    @abstractmethod
    def generate_access_token(self, identity: str) -> str:
        """Generate client SDK access token for browser-based calling."""
