# 📊 AI Boardroom: Pricing & Feature Matrix

Here is the high-level comparison of the AI Boardroom subscription tiers, structured to be easily readable and pictorial.

| 🌟 Feature / Category | 🪣 The "Sandbox" (Free) | 🎙️ The "Studio" ($5/mo) | 💼 The "Executive" ($20/mo) | 🏢 The "Syndicate" (Enterprise) |
| :--- | :--- | :--- | :--- | :--- |
| **🎯 Target Audience** | Hobbyists, Students, Testers | Solo Creators, YouTubers, Indie Hackers | Power Users, Founders, Tech Leads | B2B, Creative Agencies, Dev Firms |
| **📋 Included Templates** | 1 (Basic Writer's Room) | 5 Pre-built Templates | ♾️ ALL Templates | ♾️ ALL Templates |
| **🎭 Persona Access** | Basic (Director, Writer, Critic) | All Core + **Advanced Tech SME** | ♾️ ALL Personas | ♾️ ALL + Custom Trained Personas |
| **📚 Data & Knowledge (RAG)**| 🌐 Standard Web Search APIs | 📖 Curated Storytelling RAG Data | 📖 Curated Storytelling RAG Data | 🔐 Private Custom RAG Ingestion |
| **🚦 Request Limits** | 🛑 10 Sessions or 50 Msg / Day | 📈 50 Sessions / Day | 🚀 Uncapped / Very High | ♾️ Unlimited Custom Volume |
| **🧠 Memory Depth** | 💭 L1/L2 (Short-term context) | 🧠 L3/L4 (Continuous Memory) | 🧠 L3/L4 (Continuous Memory) | 🧠 L4+ (Persistent Team Memory) |
| **📤 Export Options** | ❌ Standard Copy/Paste | ✅ 1-Click Markdown / PDF Export | ✅ 1-Click Markdown / PDF Export | ✅ Custom API & Webhook Exports |
| **🛠️ Customization (BYOR)** | ❌ No | ❌ No | ✅ Upload Custom YAML/JSON Configs | ✅ Upload Custom YAML/JSON Configs |
| **⚙️ Advanced AI Tools** | ❌ None | ❌ None | 🐍 `execute_python_sandbox` | 🐍 Full Sandboxed Code Execution |
| **⚡ Infrastructure & Support**| ☁️ Shared | ☁️ Shared | 🏎️ Priority Server Routing | 🛡️ Dedicated Servers & SSO |
| **👥 Collaboration** | 👤 Single Player | 👤 Single Player | 👤 Single Player | 🤝 Multi-player Team Mode |

---
*Note: BYOR stands for "Bring Your Own Room" allowing advanced users to map custom interaction topologies for the AI agents.*


# AI Boardroom: Commercial Pricing & Feature Strategy

This document outlines the high-level business strategy and pricing models for the AI Boardroom SaaS application. The tiers have been uniquely named to reflect the "Boardroom" and "Production" themes, moving away from generic Free/Plus/Pro naming conventions.

---

## Tier 1: The "Sandbox" Tier (Free)
**Target Audience:** Hobbyists, students, and users wanting to test the "Debate-to-Write" mechanics before committing.
**Pricing:** $0 / month

**Core Features:**
* **Included Templates:** 1 Basic Template (Standard Writer's Room).
* **Persona Access:** Director, Writer, and Critic (Basic).
* **Data & Knowledge:** Standard web search / query APIs only. No access to the curated RAG datasets.
* **Limits:** Strict daily limit on LLM interactions (e.g., 10 "Boardroom Sessions" or 50 messages per day).
* **Memory:** Standard L1/L2 short-term memory (limited context retention).

---

## Tier 2: The "Studio" Tier (Formerly Plus)
**Target Audience:** YouTube creators, indie hackers, and solo content creators.
**Pricing:** $5 / month

**Core Features:**
* **Included Templates:** 5 Pre-built Templates (Writer’s Room, YouTube Creator Room, Product Strategy Room, Career Advisory Board, etc.).
* **Persona Access:** All core personas, including the **Advanced Tech SME**.
* **Data & Knowledge (RAG):** The Tech SME gains access to your highly-curated storytelling RAG database (Public Domain Books, Gutenberg classics, YouTube-Commons datasets, successful scripts).
* **Limits:** Significantly higher daily and monthly request limits (e.g., 50 Sessions/day).
* **Export:** 1-Click Export to clean Markdown or PDF formats.
* **Memory:** Access to L3/L4 continuous memory summarizing for long-running context retention.

---

## Tier 3: The "Executive" Tier (Formerly Pro)
**Target Audience:** Power users, serial entrepreneurs, tech leads, and heavy content engines.
**Pricing:** $20 / month

**Core Features:**
* **Included Templates:** Access to ALL templates (Startup Founder Room, Architecture Review Board, Research Lab, Investment Committee).
* **Bring Your Own Room (BYOR):** Ability to upload custom YAML/JSON room configurations. Users can define their own stages, personas, and system prompts.
* **Advanced Action Tools:** The Tech SME gets access to the `execute_python_sandbox` to run real code and verify technical facts live.
* **Limits:** Uncapped or exceptionally high API usage limits to support deep, multi-hour "Debate-to-Write" sessions.
* **Performance:** Priority server routing (faster token streaming and lower latency).

---

## Tier 4: The "Syndicate" Tier (Enterprise)
*Recommendation: Keep this strictly separate from the Pro tier. Do not bundle Enterprise into Pro.*
**Target Audience:** B2B Clients, creative agencies, software development firms.
**Pricing:** Custom Pricing ($500+ / month / organization)

**Core Features:**
* **Private Knowledge Base (Custom RAG):** Allow companies to securely ingest their own private company wikis, codebases, or proprietary data for the Tech SME to reference.
* **Self-Hosted / Dedicated Infrastructure:** Dedicated NeonDB/Redis instances to ensure data privacy and compliance.
* **Team Collaboration:** Multi-player mode where multiple human users can sit in the same AI Boardroom.
* **SSO & Admin Controls:** SAML, role-based access, and centralized billing.

---

## Additional Value Levers to Consider
To further differentiate the tiers, consider gating the following features:

1.  **Critic Impact Adjustments (Slider):** Let Studio/Executive users adjust how "harsh" or "lenient" the Critic is (modifying the `max_argument_quota`).
2.  **Concurrent Rooms:** Free users can only run 1 room at a time. Studio users can run 3. Executive users can have unlimited active rooms running asynchronous tasks.
3.  **UI Layout Customization:** Let Executive users customize their dashboard or dual-pane split-screen layouts.