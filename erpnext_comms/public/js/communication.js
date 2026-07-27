frappe.ui.form.on("Communication", {
    refresh(frm) {
        if (frm.doc.communication_medium === "WhatsApp") {
            frm.page.set_indicator(__("WhatsApp"), "green");

            if (frm.doc.phone_no) {
                frm.add_custom_button(__("Reply WhatsApp"), () => {
                    erpnext_comms.show_whatsapp_dialog(frm, frm.doc.phone_no);
                }, __("Actions"));
            }
        }
    },
});

erpnext_comms.show_whatsapp_dialog = function (frm, to_number) {
    const d = frappe.prompt(
        {fieldname: "message", fieldtype: "Text", label: "Message", reqd: 1},
        (values) => {
            erpnext_comms.CommHub.send_whatsapp(
                erpnext_comms.default_from_number,
                to_number,
                values.message,
                frm.doc.reference_doctype,
                frm.doc.reference_name,
            ).then(() => {
                frappe.show_alert({message: __("WhatsApp sent!"), indicator: "green"});
                frm.reload_doc();
            });
        },
        __("Send WhatsApp to {0}", [to_number]),
        __("Send"),
    );
};
