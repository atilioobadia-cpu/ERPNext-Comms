frappe.ui.form.on("EC Settings", {
    refresh(frm) {
        frm.page.set_indicator_badge("WhatsApp", frm.doc.whatsapp_enabled, "whatsapp_section");
        frm.page.set_indicator_badge("SMS", frm.doc.sms_enabled, "sms_section");
        frm.page.set_indicator_badge("Voice", frm.doc.voice_enabled, "voice_section");
    },
});
