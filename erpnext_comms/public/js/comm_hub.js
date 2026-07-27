frappe.provide("erpnext_comms");

erpnext_comms.CommHub = class CommHub {
    constructor() {
        this.whatsapp_status = "disconnected";
        this.init();
    }

    init() {
        frappe.realtime.on("erpnext_comms_incoming_whatsapp", (data) => {
            frappe.show_alert({
                message: __("WhatsApp from {0}: {1}", [data.from, data.body]),
                indicator: "green",
            });
        });
    }

    static send_whatsapp(from_number, to_number, message, link_doctype, link_name) {
        return frappe.xcall("erpnext_comms.api.whatsapp.send_message", {
            from_number,
            to_number,
            message,
            link_doctype,
            link_name,
        });
    }
};

erpnext_comms.comm_hub = new erpnext_comms.CommHub();
