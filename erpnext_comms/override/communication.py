"""Extend Frappe Communication doctype."""
import frappe


def after_insert(doc, method):
    """After Communication is inserted — auto-link to referenced documents."""
    if doc.communication_medium == "WhatsApp":
        _link_whatsapp_to_document(doc)


def _link_whatsapp_to_document(doc):
    """If a WhatsApp message has a phone number, try to link to Contact/Customer/Lead."""
    if not doc.phone_no:
        return

    from erpnext_comms.service.communication_service import CommunicationService
    service = CommunicationService()

    contact = service.find_contact_by_phone(doc.phone_no)
    if contact:
        already_linked = any(
            tl.link_doctype == "Contact" and tl.link_name == contact
            for tl in doc.timeline_links
        )
        if not already_linked:
            doc.append("timeline_links", {"link_doctype": "Contact", "link_name": contact})
            doc.save(ignore_permissions=True)


def get_additional_timeline_content(doc, doctype, name):
    """Show WhatsApp/SMS logs in any document's timeline."""
    results = []

    # Get WhatsApp messages linked to this document
    whatsapp_logs = frappe.get_all(
        "EC WhatsApp Message Log",
        filters={"link_doctype": doctype, "link_name": name},
        fields=["name", "direction", "from_number", "to_number", "message_body", "status", "creation"],
        order_by="creation desc",
        limit_page_length=20,
    )

    for log in whatsapp_logs:
        direction_icon = "→" if log.direction == "Outgoing" else "←"
        results.append({
            "communication_type": "WhatsApp",
            "icon": "comments",
            "color": "#25D366",
            "title": f"WhatsApp {direction_icon} {log.from_number} → {log.to_number}",
            "description": log.message_body[:200] if log.message_body else "",
            "timestamp": log.creation,
        })

    return results
