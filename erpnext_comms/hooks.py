app_name = "erpnext_comms"
app_title = "ERPNext Comms"
app_publisher = "Alpha Associates (T) Limited"
app_description = "Unified Communication Hub for ERPNext — WhatsApp, SMS, Voice, Chat, AI"
app_email = "info@alphaassociates.co.tz"
app_icon = "octicon octicon-comment-discussion"
app_color = "#00897B"
app_license = "MIT"

required_apps = ["frappe", "erpnext"]

after_install = "erpnext_comms.setup.after_install"

app_include_js = [
    "/assets/erpnext_comms/js/comm_hub.js",
    "/assets/erpnext_comms/js/communication.js",
]
app_include_css = [
    "/assets/erpnext_comms/css/comm_hub.css",
]

# Extend Communication medium options to include WhatsApp
setup_wizard_requires = []

doc_events = {
    "Communication": {
        "after_insert": "erpnext_comms.override.communication.after_insert",
    },
    "Contact": {
        "validate": "erpnext_comms.override.contact.validate",
        "after_insert": "erpnext_comms.override.contact.after_insert",
    },
}

scheduler_events = {
    "hourly": [
        "erpnext_comms.tasks.sync.sync_delivery_statuses",
    ],
    "daily": [
        "erpnext_comms.tasks.cleanup.cleanup_old_messages",
    ],
}

# Additional timeline content — show WhatsApp/SMS logs in any document timeline
additional_timeline_content = {
    "*": ["erpnext_comms.override.communication.get_additional_timeline_content"],
}

# Extend Communication doctype JS
doctype_js = {
    "Communication": "public/js/communication.js",
}

fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [["dt", "in", ["Contact"]], ["module", "=", "ERPNext Comms"]],
    },
    {
        "doctype": "Property Setter",
        "filters": [["doc_type", "=", "Communication"], ["module", "=", "ERPNext Comms"]],
    },
    {
        "doctype": "Role",
        "filters": [["role_name", "like", "EC %"]],
    },
]
