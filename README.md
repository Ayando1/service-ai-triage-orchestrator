# ⚡ Enterprise AI Service Triage & Retention Orchestrator

An end-to-end prototype designed for digital service providers and enterprise customer operations. It bridges incoming unstructured support inquiries, Large Language Models (LLM / NLP), and core IT ticketing workflows to automate incident prioritization, SLA routing, and churn risk mitigation.

---

## 🎯 Business Case & Objectives
In enterprise customer operations, manual triage of incoming tickets is slow, error-prone, and drives up Mean Time to Resolution (MTTR). Furthermore, delayed responses to dissatisfied accounts increase churn rates.

This prototype demonstrates:
- **E2E Business-to-IT Alignment:** Translating raw customer text into structured, machine-readable JSON payloads ready for CRM/ticketing platforms (e.g., Salesforce, ServiceNow, Jira).
- **Business-to-AI Innovation:** Applying LLM semantic understanding to identify technological domains (Broadband, Core Billing, Hardware), determine sentiment, and propose proactive retention actions.
- **Human-in-the-Loop Governance:** AI drafts responses and recommends workflows, while human agents retain final dispatch authority.

---

## 🏗️ Core Architecture & Pipeline

1. **Intake & Semantic Parsing:** Natural language ingestion evaluated via LLM integration with an offline, rule-based fallback engine.
2. **Prioritization & SLA Engine:** Dynamic SLA assignment (P1 Critical: 2h response window, down to P3 Standard: 48h).
3. **Automated Dispatch Routing:** Automatically flags field technician intervention for severe hardware/infrastructure failures.
4. **Structured JSON Output:** Standardized schema ensuring frictionless backend and API interoperability.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+

### Installation & Execution
```bash
# 1. Clone the repository
git clone [https://github.com/](https://github.com/)<your-username>/service-ai-triage-orchestrator.git
cd service-ai-triage-orchestrator

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch application
streamlit run app.py