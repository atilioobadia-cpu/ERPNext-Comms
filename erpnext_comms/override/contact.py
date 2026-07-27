"""Extend Frappe Contact doctype with WhatsApp number."""
import frappe


def validate(doc, method):
    """Validate Contact — ensure whatsapp_no is properly formatted."""
    if doc.whatsapp_no:
        number = doc.whatsapp_no.strip()
        if not number.startswith("+"):
            frappe.msgprint(
                frappe._("WhatsApp number should start with country code (e.g. +255...)"),
                alert=True,
            )


def after_insert(doc, method):
    """After Contact is created — link existing WhatsApp messages."""
    if doc.whatsapp_no:
        _link_existing_whatsapp_messages(doc)


def _link_existing_whatsapp_messages(doc):
    """Link any existing WhatsApp messages from this number to the new Contact."""
    if not doc.whatsapp_no:
        return

    logs = frappe.get_all(
        "EC WhatsApp Message Log",
        filters=[
            ["from_number", "like", f"%{doc.whatsapp_no[-9:]}%"],
            ["link_doctype", "is", "not set"],
        ],
        fields=["name"],
        limit_page_length=10,
    )

    for log in logs:
        frappe.db.set_value("EC WhatsApp Message Log", log.name, "link_doctype", "Contact")
        frappe.db.set_value("EC WhatsApp Message Log", log.name, "link_name", doc.name)

    if logs:
        frappe.db.commit()
