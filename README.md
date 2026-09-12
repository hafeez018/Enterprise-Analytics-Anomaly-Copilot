# Enterprise Analytics & Anomaly Copilot

### Zero-Hallucination Conversational BI • AST-Hardened Security •  Self-Healing SQL •  Statistical Anomaly Detection for Cross-Industry Enterprise Data

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini%20API-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![SQLite Sandbox](https://img.shields.io/badge/Engine-SQLite%20RO%20Sandbox-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Security Guard](https://img.shields.io/badge/Security-AST%20sqlglot%20Shield-E11D48?style=for-the-badge)](https://github.com/tobymao/sqlglot)
[![Test Suite](https://img.shields.io/badge/Testing-Pytest%2025%2B%20Passing-059669?style=for-the-badge&logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Streamlit UI](https://img.shields.io/badge/Frontend-Streamlit%20Dark%20System-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)

---

## 📌 Executive Summary & Business Problem

Modern enterprise operations—whether optimizing an assembly line in advanced manufacturing, monitoring credit default risks in fintech, tracking medication adherence in healthcare, or auditing supply chains—suffer from an acute operational bottleneck: **data silos and delayed anomaly detection**.

* **The Problem:** Non-technical domain operators (Plant Managers, Supply Chain Directors, Risk Officers, Clinical Directors) notice performance degradations days or weeks after the triggering event. Requesting root-cause data from business intelligence teams requires back-and-forth communication, custom ad-hoc query queues, and manual spreadsheet analysis.
Traditional Business Intelligence (BI) tools and emerging LLM wrappers suffer from two critical flaws: **rigid static dashboards** that cannot answer ad-hoc questions, and **arithmetic hallucinations** paired with severe **SQL injection risks**.

  
* **The Solution:** This project delivers a **domain-agnostic, plug-and-play Conversational Copilot**. Any enterprise can connect their internal relational database, issue plain-English inquiries, and receive verified analytical data, statistical anomaly flags ($\vert{}Z\vert{} > 2.0$), trend charts, and automated executive mitigation plans in seconds.

  
* **Integrity Guarantee:**  The architecture guarantees **zero mathematical hallucination**. The LLM never invents or approximates numbers and acts strictly as a semantic compiler at $T = 0.0$; all computations,outlier evaluations, and aggregations are computed deterministically by the database engine on SQLite/Pandas and verified via strict statistical math.




## 🏭 Multi-Sector Application Matrix

This platform is not constrained to consumer applications. It adapts dynamically to any domain schema:

| Industry Sector | Connected Data Entities | Target Stakeholder | Representative Prompt | Anomaly Detected ($\vert{}Z\vert{} > 2$) |
| :--- | :--- | :--- | :--- | :--- |
| **Advanced Manufacturing** | Sensors, machines, batch yields, maintenance logs | Plant Operations Manager | *"What is the hourly scrap rate on Assembly Line 4 over the last 14 days?"* | Sudden spike in defective units caused by thermal sensor drift. |
| **Supply Chain & Logistics** | Warehouses, shipments, carrier logs, inventory units | Logistics Director | *"Show daily delayed dispatches grouped by distribution center."* | Regional logistics breakdown due to unexpected fulfillment bottleneck. |
| **Fintech & Banking** | Transactions, merchant accounts, risk scores, gateways | Fraud & Risk Analyst | *"What is the daily volume of failed chargebacks by merchant tier?"* | Gateway API timeout driving a sharp drop in processed settlements. |
| **Healthcare & Pharma** | Admissions, bed occupancy, clinical audits, medication stock | Hospital Operations Lead | *"Compare average triage wait times by department over the past 3 weeks."* | ER overload correlating with specific weekend intake spikes. |
| **Digital Products & Retail** | Users, checkout funnels, subscription tiers, carts | Growth / Product Lead | *"What is the daily checkout volume by device operating system?"* | Mobile app checkout drop following a faulty production release. |

---

## 🏗️ System Architecture

```text
                 ╭───────────────────────────────╮
                 │   Natural Language Inquiry    │
                 ╰───────────────┬───────────────╯
                                 │
                                 v
╭─────────────────────────────────────────────────────────────────╮
│             Dynamic DDL Schema Introspection Engine             │
│          (Extracts user tables from catalog at runtime)         │
╰────────────────────────────────┬────────────────────────────────╯
                                 │
                                 v
╭─────────────────────────────────────────────────────────────────╮
│                     Google Gemini Compiler                      │
│      (Translates prompt into dialect-specific SQL @ T=0.0)      │
╰────────────────────────────────┬────────────────────────────────╯
                                 │
                                 v
╭─────────────────────────────────────────────────────────────────╮
│                     AST Security Guardrail                      │
│   (Parses sqlglot AST: blocks DDL/DML, snooping & injections)   │
╰────────────────────────────────┬────────────────────────────────╯
                                 │
                 ┌───────────────┴───────────────┐
              (Valid)                        (Invalid)
                 │                               │
                 v                               v
╭─────────────────────────────╮     ╭─────────────────────────────╮
│    SQLite Read-Only Lock    │     │  Autonomous Reflexion Loop  │
│    (URI file:db?mode=ro)    │     │ (Feeds compiler errors back;│
│                             │     │  self-heals up to 3 tries)  │
╰──────────────┬──────────────╯     ╰──────────────┬──────────────╯
               │                                   │
               ├<──────────────────────────────────┘
               │
               └─────────────────┐
                                 │
                                 v
╭─────────────────────────────────────────────────────────────────╮
│                 Deterministic Pandas Data Layer                 │
╰────────────────────────────────┬────────────────────────────────╯
                                 │
                 ┌───────────────┴───────────────┐
                 │                               │
                 v                               v
╭─────────────────────────────╮     ╭─────────────────────────────╮
│ Statistical Anomaly Engine  │     │ Multimodal Executive Dossier│
│  - Modified Z-Score (MAD)   │     │  - Temporal Trendline (SNS) │
│  - Two-Proportion Z-Test    │     │  - Quartile / Donut Dist.   │
│  - Standard Z-Score Fallback│     │  - Outlier Density Plot     │
╰──────────────┬──────────────╯     ╰──────────────┬──────────────╯
               │                                   │
               └─────────────────┬─────────────────┘
                                 │
                                 v
╭─────────────────────────────────────────────────────────────────╮
│            Live SVG Neural State Machine & Dashboard            │
╰─────────────────────────────────────────────────────────────────╯
```
