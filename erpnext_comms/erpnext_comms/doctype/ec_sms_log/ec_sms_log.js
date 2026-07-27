frappe.ui.form.on("EC SMS Log", {
    refresh(frm) {
        if (frm.doc.link_doctype && frm.doc.link_name) {
            frm.add_custom_button(__("Open {0}", [frm.doc.link_doctype]), () => {
                frappe.set_route("Form", frm.doc.link_doctype, frm.doc.link_name);
            }, __("Navigate"));
        }
    },
});
