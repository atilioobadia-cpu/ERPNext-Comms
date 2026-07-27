frappe.ui.form.on("EC WhatsApp Message Log", {
    refresh(frm) {
        if (frm.doc.link_doctype && frm.doc.link_name) {
            frm.add_custom_button(__("Open {0}", [frm.doc.link_doctype]), () => {
                frappe.set_route("Form", frm.doc.link_doctype, frm.doc.link_name);
            }, __("Navigate"));
        }
        if (frm.doc.communication) {
            frm.add_custom_button(__("Open Communication"), () => {
                frappe.set_route("Form", "Communication", frm.doc.communication);
            }, __("Navigate"));
        }
    },
});
