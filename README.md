# ERPNext Comms

**Unified Communication Hub for ERPNext — WhatsApp, SMS, Voice, Chat, AI**

[![Frappe Framework](https://img.shields.io/badge/Built%20with-Frappe%20Framework-00897B)](https://frappeframework.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.0.1-blue.svg)](https://github.com/atilioobadia-cpu/ERPNext-Comms)

---

## Overview

ERPNext Comms is a standalone Frappe application that unifies WhatsApp, SMS, Voice, Email, and AI-powered messaging into a single communication hub for ERPNext. Built on the adapter pattern, it provides a provider-agnostic architecture that can switch between Twilio, WhatsApp Cloud API, local SMS providers, and more — without changing application logic.

### Key Capabilities

- **Multi-Channel Messaging** — WhatsApp, SMS, Voice, and Email from one interface
- **Auto-Linking** — Communications automatically attach to Tasks, Projects, and other documents via pattern matching (`#TASK-XXXXX`, `#PRJ-XXXXX`)
- **Role-Based Visibility** — Employees see communications only for their assigned projects
- **Employee Summaries** — Track communication activity per employee across all channels
- **Timeline Integration** — WhatsApp and SMS logs appear in any document's timeline
- **Adapter Architecture** — Swap providers (Twilio, Meta, Beem Africa) without code changes
- **Real-Time Notifications** — Incoming messages appear instantly via Socket.IO
- **Media Support** — Send and receive images, documents, audio, and video
- **Message Templates** — Reusable templates with variable substitution
- **Delivery Tracking** — Real-time status updates (Sent → Delivered → Read)

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  ERPNext Comms                   │
├─────────────┬──────────────┬────────────────────┤
│  API Layer  │  Service Layer │  Adapter Layer    │
│  (Webhooks) │  (Orchestrate) │  (Provider SDK)  │
├─────────────┴──────────────┴────────────────────┤
│              Frappe Communication                │
│           (Extended with WhatsApp)               │
├─────────────────────────────────────────────────┤
│  EC WhatsApp Log │ EC SMS Log │ EC Message Tmpl │
│  EC Settings     │ EC Provider│ Contact + Roles  │
└─────────────────────────────────────────────────┘
```

### Design Principles

1. **Never Duplicate** — Extend Frappe's existing Communication doctype; create new DocTypes only where nothing exists
2. **Adapter Pattern** — All provider integrations implement base interfaces (`BaseWhatsAppAdapter`, `BaseSMSAdapter`, `BaseVoiceAdapter`)
3. **Service Layer** — Business logic lives in services, not in API endpoints or DocType controllers
4. **Provider Agnostic** — Switch from Twilio to Meta Cloud API by swapping one adapter file

---

## DocTypes

| DocType | Purpose |
|---------|---------|
| **EC Settings** | Global configuration — enable/disable channels, set defaults |
| **EC Provider** | Provider credentials (Twilio, Meta, Beem Africa, etc.) |
| **EC WhatsApp Message Log** | Full WhatsApp message audit trail with auto-linking |
| **EC SMS Log** | SMS message audit trail |
| **EC Message Template** | Reusable message templates with variables |

---

## Roles

| Role | Access |
|------|--------|
| **EC Manager** | Full access — settings, providers, all logs, templates |
| **EC Agent** | Send/receive messages, view own logs |
| **EC Viewer** | Read-only access to logs and reports |

---

## Installation

### Prerequisites

- Frappe Framework v14+ / ERPNext v14+
- Python 3.10+
- Twilio account (for WhatsApp/Voice) or WhatsApp Cloud API credentials

### Install

```bash
# Clone the app
bench get-app https://github.com/atilioobadia-cpu/ERPNext-Comms.git

# Install on your site
bench --site your-site.local install-app erpnext_comms

# Build assets
bench build --app erpnext_comms

# Migrate
bench --site your-site.local migrate
```

### Post-Installation Setup

1. **EC Settings** — Enable WhatsApp/SMS/Voice channels and set default from number
2. **EC Provider** — Add your Twilio credentials (Account SID, Auth Token, phone number)
3. **Roles** — Assign `EC Manager`, `EC Agent`, or `EC Viewer` to users
4. **Contact** — Add WhatsApp numbers to Contact records via the new `whatsapp_no` field
5. **Webhooks** — Configure Twilio WhatsApp webhook URL:
   ```
   https://your-site.local/api/method/erpnext_comms.api.whatsapp.incoming_message
   ```

---

## API Endpoints

### WhatsApp

| Endpoint | Method | Description |
|----------|--------|-------------|
| `erpnext_comms.api.whatsapp.incoming_message` | POST (guest) | Twilio webhook for incoming WhatsApp messages |
| `erpnext_comms.api.whatsapp.status_update` | POST (guest) | Twilio webhook for delivery status updates |
| `erpnext_comms.api.whatsapp.send_message` | POST | Send a WhatsApp message from ERPNext |

### Auto-Linking Patterns

Communications are automatically linked to documents when these patterns appear in the message body:

| Pattern | Document Type |
|---------|--------------|
| `#TASK-2026-00123` | Task |
| `#PRJ-2026-0001` | Project |
| `#ORIG-2026-0001` | Alpha Assignment Origination |
| `#ISSUE-2026-0001` | Issue |

---

## Companion Apps

ERPNext Comms is designed to work alongside these apps for a complete communication stack:

| App | Purpose | Repository |
|-----|---------|------------|
| **whatsapp\_chat** | Real-time WhatsApp chat UI in Frappe Desk | [ERPNext-whatsapp](https://github.com/atilioobadia-cpu/ERPNext-whatsapp) |
| **frappe\_whatsapp** | WhatsApp Cloud API core integration (dependency of whatsapp\_chat) | [frappe\_whatsapp](https://github.com/shridarpatil/frappe_whatsapp) |
| **telephony** | TP Call Log, Twilio voice handling | Bundled with ERPNext |

### Installed Together

```bash
# 1. Core WhatsApp Cloud API
bench get-app https://github.com/shridarpatil/frappe_whatsapp.git
bench --site your-site install-app frappe_whatsapp

# 2. WhatsApp Chat UI
bench get-app https://github.com/atilioobadia-cpu/ERPNext-whatsapp.git
bench --site your-site install-app whatsapp_chat

# 3. ERPNext Comms (backend hub)
bench get-app https://github.com/atilioobadia-cpu/ERPNext-Comms.git
bench --site your-site install-app erpnext_comms
```

---

## Development

### Project Structure

```
erpnext_comms/
├── hooks.py                  # App hooks (events, scheduler, fixtures)
├── setup.py                  # After-install setup (roles, permissions, custom fields)
├── modules.txt               # Frappe module definition
├── adapter/                  # Provider adapters (abstract + implementations)
│   ├── base.py               # BaseWhatsAppAdapter, BaseSMSAdapter, BaseVoiceAdapter
│   └── twilio_whatsapp.py    # Twilio WhatsApp implementation
├── api/                      # API endpoints (webhooks, send)
│   └── whatsapp.py           # WhatsApp incoming/status/send handlers
├── service/                  # Business logic layer
│   ├── communication_service.py  # Core: create, auto-link, phone lookup
│   └── whatsapp_service.py       # WhatsApp lifecycle management
├── override/                 # Frappe doctype extensions
│   ├── communication.py      # Auto-link, timeline content
│   └── contact.py            # WhatsApp number on Contact
├── tasks/                    # Scheduled jobs
│   ├── sync.py               # Hourly delivery status sync
│   └── cleanup.py            # Daily old message cleanup
├── erpnext_comms/doctype/    # Frappe DocTypes
│   ├── ec_settings/          # Global settings (single)
│   ├── ec_provider/          # Provider credentials
│   ├── ec_whatsapp_message_log/  # WhatsApp audit trail
│   ├── ec_sms_log/           # SMS audit trail
│   └── ec_message_template/  # Reusable templates
├── erpnext_comms/workspace/  # Desk workspace
│   └── communication_hub/    # EC Manager workspace
├── public/                   # Frontend assets
│   ├── js/comm_hub.js        # Real-time notifications
│   ├── js/communication.js   # WhatsApp reply UI on Communication
│   └── css/comm_hub.css      # Channel indicator styles
└── config/                   # Frappe config
    ├── desktop.py            # Module entry
    └── docs.py               # Documentation config
```

### Adding a New Provider

1. Create `adapter/your_provider.py`
2. Implement `BaseWhatsAppAdapter`, `BaseSMSAdapter`, or `BaseVoiceAdapter`
3. Add an `EC Provider` record in the desk
4. No changes needed to service or API layers

### Running Tests

```bash
bench --site your-site.local run-tests --app erpnext_comms
```

---

## Roadmap

- [ ] Voice call integration (Twilio BYOC)
- [ ] SMS integration (Beem Africa / NextSMS for Tanzania)
- [ ] AI-powered auto-replies (OpenAI / Anthropic / Ollama)
- [ ] WhatsApp template messages (pre-approved Meta templates)
- [ ] Bulk messaging with rate limiting
- [ ] Communication analytics dashboard
- [ ] Email channel integration (IMAP/SMTP)
- [ ] Call recording and transcription
- [ ] Multi-language message templates

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Author

**Alpha Associates (T) Limited**
- Email: info@alphaassociates.co.tz
- Website: alphaassociates.co.tz

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
