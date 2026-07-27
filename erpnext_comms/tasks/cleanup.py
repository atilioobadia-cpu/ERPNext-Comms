"""Scheduled cleanup tasks."""
import frappe


def cleanup_old_messages():
    """Daily: archive old message logs beyond retention period."""
    retention_days = frappe.db.get_single_value("EC Settings", "retention_days") or 365
    cutoff = frappe.utils.add_days(frappe.utils.nowdate(), -retention_days)

    for doctype in ["EC WhatsApp Message Log", "EC SMS Log"]:
        old = frappe.get_all(
            doctype,
            filters={"creation": ["<", cutoff]},
            fields=["name"],
            limit_page_length=100,
        )
        for doc in old:
            frappe.delete_doc(doctype, doc.name, ignore_permissions=True, force=True)

        if old:
            frappe.db.commit()
