import frappe


def after_install():
    _create_roles()
    _create_permissions()
    _create_custom_fields()
    _create_property_setters()
    _create_ec_settings()
    frappe.db.commit()


def _create_roles():
    roles = [
        {"role_name": "EC Manager", "desk_access": 1, "is_custom": 1, "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1},
        {"role_name": "EC Agent", "desk_access": 1, "is_custom": 1, "read": 1, "write": 1, "create": 1, "report": 1},
        {"role_name": "EC Viewer", "desk_access": 1, "is_custom": 1, "read": 1, "report": 1},
    ]
    for role_data in roles:
        if not frappe.db.exists("Role", role_data["role_name"]):
            frappe.get_doc({"doctype": "Role", **role_data}).insert(ignore_permissions=True)


def _create_permissions():
    perms = {
        "EC Settings": [{"role": "EC Manager", "read": 1, "write": 1}],
        "EC Provider": [{"role": "EC Manager", "read": 1, "write": 1, "create": 1, "delete": 1}],
        "EC WhatsApp Message Log": [
            {"role": "EC Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1},
            {"role": "EC Agent", "read": 1, "write": 1, "create": 1, "report": 1},
            {"role": "EC Viewer", "read": 1, "report": 1},
        ],
        "EC SMS Log": [
            {"role": "EC Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1},
            {"role": "EC Agent", "read": 1, "write": 1, "create": 1, "report": 1},
            {"role": "EC Viewer", "read": 1, "report": 1},
        ],
        "EC Message Template": [
            {"role": "EC Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
            {"role": "EC Agent", "read": 1},
        ],
    }
    for dt, role_perms in perms.items():
        for p in role_perms:
            if not frappe.db.exists("Custom DocPerm", {"parent": dt, "role": p["role"]}):
                frappe.get_doc({
                    "doctype": "Custom DocPerm",
                    "parent": dt,
                    "parenttype": "DocType",
                    "parentfield": "permissions",
                    **p,
                }).insert(ignore_permissions=True)


def _create_custom_fields():
    custom_fields = {
        "Contact": [
            {
                "fieldname": "whatsapp_no",
                "fieldtype": "Data",
                "label": "WhatsApp Number",
                "insert_after": "mobile_no",
                "module": "ERPNext Comms",
            },
        ],
    }
    for dt, fields in custom_fields.items():
        for field in fields:
            if not frappe.db.exists("Custom Field", {"dt": dt, "fieldname": field["fieldname"]}):
                frappe.get_doc({
                    "doctype": "Custom Field",
                    "dt": dt,
                    "module": "ERPNext Comms",
                    "owner": "Administrator",
                    **field,
                }).insert(ignore_permissions=True)


def _create_property_setters():
    # Add WhatsApp to Communication.communication_medium options
    if not frappe.db.exists("Property Setter", {
        "doc_type": "Communication",
        "field_name": "communication_medium",
        "property": "options",
    }):
        frappe.get_doc({
            "doctype": "Property Setter",
            "doc_type": "Communication",
            "field_name": "communication_medium",
            "property": "options",
            "value": "\nEmail\nChat\nPhone\nSMS\nWhatsApp\nEvent\nMeeting\nVisit\nOther",
            "module": "ERPNext Comms",
        }).insert(ignore_permissions=True)


def _create_ec_settings():
    if not frappe.db.exists("EC Settings", "EC Settings"):
        frappe.get_doc({
            "doctype": "EC Settings",
            "enabled": 1,
        }).insert(ignore_permissions=True)
