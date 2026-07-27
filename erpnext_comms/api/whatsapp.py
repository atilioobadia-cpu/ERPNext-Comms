"""WhatsApp API — webhook handlers and send endpoints."""
import frappe
from frappe import _
from werkzeug.wrappers import Response

from erpnext_comms.service.whatsapp_service import WhatsAppService


@frappe.whitelist(allow_guest=True)
def incoming_message(**kwargs):
    """Webhook: Twilio sends this when a WhatsApp message arrives."""
    service = WhatsAppService()
    result = service.handle_inbound(frappe._dict(kwargs))
    return Response('<?xml version="1.0" encoding="UTF-8"?><Response></Response>', mimetype="text/xml")


@frappe.whitelist(allow_guest=True)
def status_update(**kwargs):
    """Webhook: Twilio sends this when message delivery status changes."""
    service = WhatsAppService()
    service.handle_status_update(frappe._dict(kwargs))
    return {}


@frappe.whitelist()
def send_message(from_number, to_number, message, link_doctype=None, link_name=None, media_url=None):
    """API: Send a WhatsApp message from ERPNext UI."""
    service = WhatsAppService()
    result = service.send_message(
        from_number=from_number,
        to_number=to_number,
        message=message,
        link_doctype=link_doctype,
        link_name=link_name,
        media_url=media_url,
    )
    if not result.get("ok"):
        frappe.throw(_("Failed to send: {0}").format(result.get("error", "Unknown error")))
    return result
