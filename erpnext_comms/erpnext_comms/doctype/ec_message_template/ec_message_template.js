frappe.ui.form.on("EC Message Template", {
    refresh(frm) {
        if (frm.doc.channel === "WhatsApp" && frm.doc.template_id) {
            frm.add_custom_button(__("Preview"), () => {
                frappe.msgprint(__("Template ID: {0}", [frm.doc.template_id]));
            });
        }
    },
});
