"""Scheduled sync tasks."""
import frappe


def sync_delivery_statuses():
    """Hourly: sync delivery statuses for outgoing messages."""
    # Sync WhatsApp message delivery statuses from Twilio
    pending = frappe.get_all(
        "EC WhatsApp Message Log",
        filters={"direction": "Outgoing", "status": ["in", ["Sent"]]},
        fields=["name", "message_id"],
        limit_page_length=50,
    )

    for msg in pending:
        # Could query Twilio API for status updates
        # For now, rely on webhook callbacks
        pass
