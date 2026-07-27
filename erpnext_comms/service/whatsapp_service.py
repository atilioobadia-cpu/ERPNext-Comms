"""WhatsApp Service — orchestrates WhatsApp operations using adapters."""
import frappe

from erpnext_comms.adapter.base import BaseWhatsAppAdapter


class WhatsAppService:
    """High-level WhatsApp operations."""

    def __init__(self, adapter: BaseWhatsAppAdapter = None):
        self.adapter = adapter or self._load_adapter()

    def _load_adapter(self):
        from erpnext_comms.adapter.twilio_whatsapp import TwilioWhatsAppAdapter
        return TwilioWhatsAppAdapter()

    def handle_inbound(self, webhook_data: dict) -> dict:
        """Process incoming WhatsApp message. Creates Communication + EC WhatsApp Message Log."""
        from erpnext_comms.service.communication_service import CommunicationService
        comm_service = CommunicationService()

        parsed = self.adapter.handle_inbound(webhook_data)

        # Find linked document
        ref_doctype, ref_name = comm_service.get_linked_doctype(parsed["from_number"])

        # Create Communication record
        comm = comm_service.create_communication(
            channel="WhatsApp",
            direction="Received",
            from_addr=parsed["from_number"],
            to_addr=parsed["to_number"],
            content=parsed["body"],
            phone_no=parsed["from_number"],
            reference_doctype=ref_doctype,
            reference_name=ref_name,
        )

        # Auto-link via content patterns (#TASK-XXX)
        linked = comm_service.auto_link(
            parsed["body"],
            parsed["from_number"],
            parsed["to_number"],
            comm.name,
        )

        # Determine agent
        agent = self._find_agent(parsed["to_number"])

        # Create EC WhatsApp Message Log
        log = frappe.get_doc({
            "doctype": "EC WhatsApp Message Log",
            "message_id": parsed["message_id"],
            "direction": "Incoming",
            "from_number": parsed["from_number"],
            "to_number": parsed["to_number"],
            "message_body": parsed["body"],
            "media_url": parsed.get("media_url", ""),
            "status": "Received",
            "received_at": frappe.utils.now_datetime(),
            "agent": agent,
            "communication": comm.name,
            "link_doctype": ref_doctype,
            "link_name": ref_name,
        })
        log.insert(ignore_permissions=True)
        frappe.db.commit()

        # Realtime notification
        frappe.publish_realtime("erpnext_comms_incoming_whatsapp", {
            "from": parsed["from_number"],
            "body": parsed["body"][:100],
            "message_id": parsed["message_id"],
        })

        return {"ok": True, "communication": comm.name, "log": log.name}

    def send_message(self, from_number, to_number, message, link_doctype=None, link_name=None, media_url=None):
        """Send WhatsApp message. Creates Communication + EC WhatsApp Message Log."""
        from erpnext_comms.service.communication_service import CommunicationService
        comm_service = CommunicationService()

        result = self.adapter.send_message(from_number, to_number, message, media_url)

        if not result.get("ok"):
            return result

        # Create Communication record
        comm = comm_service.create_communication(
            channel="WhatsApp",
            direction="Sent",
            from_addr=from_number,
            to_addr=to_number,
            content=message,
            phone_no=to_number,
            reference_doctype=link_doctype,
            reference_name=link_name,
            agent=frappe.session.user,
        )

        # Auto-link via content
        comm_service.auto_link(message, from_number, to_number, comm.name)

        # Create EC WhatsApp Message Log
        log = frappe.get_doc({
            "doctype": "EC WhatsApp Message Log",
            "message_id": result["message_id"],
            "direction": "Outgoing",
            "from_number": from_number,
            "to_number": to_number,
            "message_body": message,
            "media_url": media_url or "",
            "status": "Sent",
            "sent_at": frappe.utils.now_datetime(),
            "agent": frappe.session.user,
            "communication": comm.name,
            "link_doctype": link_doctype,
            "link_name": link_name,
        })
        log.insert(ignore_permissions=True)
        frappe.db.commit()

        return {"ok": True, "communication": comm.name, "log": log.name, "message_id": result["message_id"]}

    def handle_status_update(self, webhook_data: dict):
        """Update message delivery/read status."""
        parsed = self.adapter.handle_status_update(webhook_data)
        message_id = parsed.get("message_id")
        if not message_id:
            return

        if frappe.db.exists("EC WhatsApp Message Log", message_id):
            frappe.db.set_value("EC WhatsApp Message Log", message_id, "status", parsed["status"])
            frappe.db.commit()

    def _find_agent(self, phone_number):
        """Find user assigned to this WhatsApp number."""
        phone = "".join(c for c in phone_number if c.isdigit() or c == "+")
        agents = frappe.get_all(
            "EC Provider",
            filters={"provider_type": "WhatsApp", "enabled": 1},
            fields=["name"],
        )
        return frappe.session.user if frappe.session.user != "Guest" else None
