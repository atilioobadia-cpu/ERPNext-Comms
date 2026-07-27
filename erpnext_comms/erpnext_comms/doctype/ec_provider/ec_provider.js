frappe.ui.form.on("EC Provider", {
    provider_type(frm) {
        if (frm.doc.provider_type === "WhatsApp") {
            frm.set_value("webhook_base_url", "https://aims.alphaerp.tz/api/method/erpnext_comms.api.whatsapp.incoming_message");
        }
    },
});
