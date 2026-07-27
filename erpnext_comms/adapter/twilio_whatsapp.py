import frappe
from twilio.rest import Client as TwilioClient

from .base import BaseWhatsAppAdapter


class TwilioWhatsAppAdapter(BaseWhatsAppAdapter):
    """WhatsApp adapter using Twilio WhatsApp Business API."""

    def __init__(self, provider_doc=None):
        if provider_doc:
            self.provider = provider_doc
        else:
            self.provider = self._get_provider()

    def _get_provider(self):
        return frappe.get_doc("EC Provider", {"provider_type": "WhatsApp", "provider_name": "Twilio", "enabled": 1})

    def _get_client(self):
        auth_token = self.provider.get_password("auth_token")
        return TwilioClient(self.provider.account_sid, auth_token)

    def handle_inbound(self, webhook_data: dict) -> dict:
        from_number = self.normalize_number(webhook_data.get("From", ""))
        to_number = self.normalize_number(webhook_data.get("To", ""))
        body = webhook_data.get("Body", "")
        message_sid = webhook_data.get("MessageSid", "")
        num_media = int(webhook_data.get("NumMedia", 0) or 0)
        media_url = webhook_data.get("MediaUrl0", "") if num_media > 0 else ""

        return {
            "message_id": message_sid,
            "from_number": from_number,
            "to_number": to_number,
            "body": body,
            "media_url": media_url,
            "channel": "WhatsApp",
            "direction": "Incoming",
            "status": "Received",
        }

    def send_message(self, from_number: str, to_number: str, message: str, media_url: str = None) -> dict:
        client = self._get_client()
        twilio_from = f"whatsapp:{from_number}"
        twilio_to = f"whatsapp:{to_number}"

        kwargs = {"body": message, "from_": twilio_from, "to": twilio_to}
        if media_url:
            kwargs["media_url"] = [media_url]

        msg = client.messages.create(**kwargs)
        return {"ok": True, "message_id": msg.sid, "status": msg.status}

    def handle_status_update(self, webhook_data: dict) -> dict:
        status_map = {
            "queued": "Sent",
            "sent": "Sent",
            "delivered": "Delivered",
            "read": "Read",
            "failed": "Failed",
            "undelivered": "Failed",
        }
        raw_status = webhook_data.get("MessageStatus", "")
        return {
            "message_id": webhook_data.get("MessageSid", ""),
            "status": status_map.get(raw_status, raw_status.title()),
            "raw_status": raw_status,
        }

    def send_template(self, from_number: str, to_number: str, template_name: str, variables: dict = None) -> dict:
        client = self._get_client()
        content_sid = variables.get("content_sid", "") if variables else ""
        content_variables = variables.get("content_variables", {}) if variables else {}

        msg = client.messages.create(
            from_=f"whatsapp:{from_number}",
            to=f"whatsapp:{to_number}",
            content_sid=content_sid,
            content_variables=content_variables,
        )
        return {"ok": True, "message_id": msg.sid, "status": msg.status}
