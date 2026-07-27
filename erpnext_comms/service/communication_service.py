"""Core Communication Service — creates records, links to documents, builds timelines."""
import re

import frappe


class CommunicationService:
    """Central service for all communication operations."""

    def create_communication(self, channel, direction, from_addr, to_addr, content,
                             subject=None, reference_doctype=None, reference_name=None,
                             phone_no=None, attachments=None, agent=None):
        """Create a Communication record. Returns the Communication doc."""

        comm = frappe.get_doc({
            "doctype": "Communication",
            "communication_medium": channel,
            "communication_type": "Communication",
            "sent_or_received": direction,
            "sender": from_addr if direction == "Received" else (agent or frappe.session.user),
            "recipients": to_addr if direction == "Sent" else "",
            "phone_no": phone_no or (to_addr if channel in ("Phone", "SMS", "WhatsApp") else ""),
            "content": content,
            "subject": subject or f"{channel}: {from_addr} -> {to_addr}",
            "status": "Open",
        })

        if reference_doctype and reference_name:
            comm.append("timeline_links", {
                "link_doctype": reference_doctype,
                "link_name": reference_name,
            })

        comm.insert(ignore_permissions=True)
        frappe.db.commit()
        return comm

    def auto_link(self, content, from_addr, to_addr, comm_name=None):
        """Auto-detect references in content and link communication.

        Supports:
        - #TASK-2026-00123 → links to Task
        - #PRJ-2026-0001 → links to Project
        """
        if not content:
            return []

        linked = []
        patterns = [
            (r"#(TASK-[\w-]+)", "Task"),
            (r"#(PRJ-[\w-]+)", "Project"),
            (r"#(ORIG-[\w-]+)", "Alpha Assignment Origination"),
            (r"#(ISSUE-[\w-]+)", "Issue"),
        ]

        for pattern, doctype in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                docname = match.group(1).upper()
                if frappe.db.exists(doctype, docname):
                    if comm_name:
                        self.link_to_document(comm_name, doctype, docname)
                    linked.append({"doctype": doctype, "name": docname})

        return linked

    def link_to_document(self, comm_name, doctype, name):
        """Link a Communication to any document via Communication Link."""
        comm = frappe.get_doc("Communication", comm_name)

        for link in comm.timeline_links:
            if link.link_doctype == doctype and link.link_name == name:
                return

        comm.append("timeline_links", {"link_doctype": doctype, "link_name": name})
        comm.save(ignore_permissions=True)
        frappe.db.commit()

    def find_contact_by_phone(self, phone_number):
        """Find a Contact record matching the given phone number."""
        phone = "".join(c for c in phone_number if c.isdigit() or c == "+")

        contacts = frappe.get_all(
            "Contact Phone",
            filters={"phone": ["like", f"%{phone[-9:]}%"]},
            fields=["parent"],
            limit_page_length=1,
        )
        if contacts:
            return contacts[0].parent

        contacts = frappe.get_all(
            "Contact",
            filters={"whatsapp_no": ["like", f"%{phone[-9:]}%"]},
            fields=["name"],
            limit_page_length=1,
        )
        if contacts:
            return contacts[0].name

        return None

    def get_linked_doctype(self, phone_number):
        """Resolve which DocType a phone number is linked to (Contact → linked docs)."""
        contact_name = self.find_contact_by_phone(phone_number)
        if not contact_name:
            return None, None

        links = frappe.get_all(
            "Dynamic Link",
            filters={"parenttype": "Contact", "parent": contact_name},
            fields=["link_doctype", "link_name"],
            limit_page_length=1,
        )
        if links:
            return links[0].link_doctype, links[0].link_name

        return "Contact", contact_name
