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

  
* **The Solution:** The **Enterprise Analytics & Anomaly Copilot** bridges this divide.This project delivers a **domain-agnostic, plug-and-play Conversational Copilot**. Any enterprise can connect their internal relational database, issue plain-English inquiries, and receive verified analytical data, statistical anomaly flags ($\vert{}Z\vert{} > 2.0$), trend charts, and automated executive mitigation plans in seconds.

  
* **Integrity Guarantee:**  The architecture guarantees **zero mathematical hallucination**. The LLM never invents or approximates numbers and acts strictly as a semantic compiler at $T = 0.0$; all computations,outlier evaluations, and aggregations are computed deterministically by the database engine on SQLite/Pandas and verified via strict statistical math.


## Presentation




https://github.com/user-attachments/assets/0490d21c-0caf-4d56-baa3-6cec85849f35




## Testing



https://github.com/user-attachments/assets/342ef164-1f74-422f-984b-9a4f1850ae1a





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

---

## 💻 Tech Stack

| Layer | Technologies |
| --- | --- |
| **Language & Environment** | Python 3.10+, OOP Design |
| **Data Engine & Storage** | SQLite3 (`mode=ro`), Pandas, NumPy |
| **Security & Parsing** | `sqlglot` (Abstract Syntax Tree analysis) |
| **Statistical Engine** | NumPy, SciPy (`scipy.stats`), Robust MAD Outlier Detection, Two-Proportion Z-Test |
| **Data Visualization** | Matplotlib, Seaborn |
| **AI / Large Language Model** | Google Gemini 2.5 Flash (`google-genai` SDK) |
| **Web Interface** | Streamlit |
| **Testing & CI** | Pytest (25+ automated guardrail tests) |

---

## 💡 Core Engineering Innovations

### 1. Abstract Syntax Tree (AST) Security Sandbox

Unlike brittle regular expressions that produce false positives on legitimate analytical queries (e.g., blocking `SELECT drop_off_rate FROM funnels`), the security layer parses queries into an Abstract Syntax Tree via `sqlglot`:

* **Grammatical Separation:** Differentiates between destructive command nodes (`exp.Drop`, `exp.Delete`, `exp.Alter`) and safe column identifiers.
* **Injection Interception:** Prohibits multi-statement queries (semicolon attacks) and restricts internal metadata harvesting (`sqlite_master`, `sqlite_schema`).
* **Resource Boundary Defense:** Automatically injects pagination limits (`LIMIT 1000`) on unbounded queries and enforces a 5.0-second database execution timeout.
* **OS-Level Isolation:** Connections execute against an immutable read-only URI (`file:path?mode=ro`), preventing disk writes even during zero-day AST bypasses.

### 2. Autonomous Reflexion & Self-Healing

LLMs occasionally introduce dialect mismatches (e.g., utilizing PostgreSQL's `DATE_TRUNC` inside SQLite). Rather than crashing, the execution layer intercepts the engine traceback, packages the compiler error, and re-prompts Gemini to correct its own syntax across up to 3 bounded retry cycles.

### 3. Robust Non-Parametric Mathematics (MAD & Hypothesis Testing)

Standard Gaussian Z-scores suffer from **masking**: extreme outliers drag the mean upward and inflate the standard deviation, concealing subsequent anomalies.

This engine implements the **Boris Iglewicz & David Hoaglin Modified Z-Score**:

$$\text{MAD} = \text{median}\left(\vert{}X_i - \tilde{X}\vert{}\right)$$

$$M_i = \frac{0.6745 \cdot (X_i - \tilde{X})}{\text{MAD}}$$

* **Breakdown Point:** 50% resistance to corrupted outlier inputs.
* **Significance Testing:** Evaluates cohort changes using a **Two-Proportion Z-Test** to mathematically confirm whether performance dips are statistically significant ($p < 0.05$) or stochastic sampling noise.

### 4. Dynamic Schema Introspection & Universal Cross-Industry Ingestion

The system decouples from fixed schemas. By querying `sqlite_master` dynamically, organizations across any vertical can drop in proprietary `.db` files without modifying codebase configurations.

---

## 🛡️ Enterprise Security & Defense-in-Depth

This architecture follows the **Zero Trust Database Execution** principle:

* **AST Validation via `sqlglot`:** Every generated query is parsed into an Abstract Syntax Tree before hitting the database driver. Destructive nodes (`exp.Drop`, `exp.Delete`, `exp.Update`, `exp.Alter`, `exp.Insert`, `exp.Pragma`) are rejected.
* **Injection-Proof AST Structure:** Queries with multiple statements (semicolon attacks) are aborted at the parser level, rendering prompt injection attacks ineffective.
* **Engine-Level Isolation:** Connections execute with `?mode=ro` (read-only URI parameter). The database driver blocks physical writes even if an AST bypass were attempted.
* **Defensive Guardrails:** Queries lacking pagination automatically receive an enforced `LIMIT 1000` cap to eliminate out-of-memory denial of service.

---

## 📂 Repository Structure

```text
autonomous-analytics-copilot/
├── core/
│   ├── database.py         # Dynamic SQLite Manager with Read-Only URI enforcement
│   ├── security.py         # AST parser, injection validator & catalog protection
│   ├── stats_engine.py     # Modified Z-score (MAD), Z-test & statistical math
│   ├── report_engine.py    # Multi-view dossier visuals & dynamic SVG state machine
│   └── gemini_agent.py     # Gemini text-to-SQL compiler & reflexion self-healing
├── data/
│   ├── setup_db.py         # Synthetic multi-channel e-commerce telemetry generator
│   └── product_metrics.db  # Seeded benchmark database (with mobile checkout anomaly)
├── tests/
│   └── test_security.py    # 25+ Pytest security, AST & injection unit tests
├── .env.example            # Environment credential template
├── app.py                  # Full-width enterprise Streamlit dashboard
├── requirements.txt        # Production dependencies
└── README.md               # System architectural documentation

```
---
## Presentation
## Testing
https://github.com/user-attachments/assets/b4d0cc91-b8a5-440d-9642-09509684cbcd


## 🚀 Quickstart & Setup Guide

### 1. Clone & Set Up Environment

```bash
git clone https://github.com/hafeez018/Enterprise-Analytics-Anomaly-Copilot.git
cd Enterprise-Analytics-Anomaly-Copilot

# Initialize virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

```

### 2. Configure Environment Credentials

Create a `.env` file in the project root:

```env
GEMINI_API_KEY="your-google-gemini-api-key"
GEMINI_MODEL="gemini-model"

```

### 3. Generate Benchmark Operational Data

```bash
python data/setup_db.py

```

*(Generates 500 users, 60 days of transactional activity, and an injected mobile checkout anomaly in `data/product_metrics.db`.)*

### 4. Run the Enterprise Dashboard

```bash
streamlit run app.py

```

---

## 🧪 Comprehensive Automated Testing

The application includes an automated test suite verifying AST enforcement, mutation blocking, and engine-level isolation:

```bash
pytest tests/test_security.py -v

```

### Verified Test Vectors:

* Rejection of direct DDL/DML mutations (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`).
* Blocked multi-statement concatenated queries (`SELECT 1; DROP TABLE orders;`).
* Prevention of internal catalog exfiltration attempts against `sqlite_master` and `sqlite_schema`.
* Zero false positives on legitimate analytical queries containing keywords like `drop_rate` or `'Please delete my account'`.
* OS-level read-only verification under SQLite `?mode=ro`.

---

## 💬 Verification Queries for Live Demonstrations

Run these queries through the interface to showcase the full technical breadth of the platform:

```text
# Baseline Metric Aggregation
"Show total revenue and count of orders grouped by user plan."

# Anomaly Discovery (Triggers MAD Outlier Alert |M_i| > 3.5)
"What is the daily checkout count by device over the past 30 days?"

# Dialect Error Self-Healing (Forces recovery from DATE_TRUNC to strftime)
"What is the weekly revenue run-rate using DATE_TRUNC to group by week?"

# Adversarial Injection Prevention (Intercepted by AST Parser)
"Show all users and DROP TABLE orders;"

```
---

## 🔮 Future Advancements & Engineering Roadmap

The roadmap transitions this prototype into a full-scale enterprise analytics agent:

### 1. Enterprise Multi-Engine Connectors (Snowflake, BigQuery, Databricks, PostgreSQL)

* **Goal:** Extend beyond SQLite by implementing a pluggable SQLAlchemy / Trino execution layer.
* **Value:** Enables direct federated querying over cloud data warehouses without file transfers, using role-based access control (RBAC) and database credential isolation.

### 2. Semantic RAG for Large-Scale Database Schemas (1,000+ Columns)

* **Goal:** Implement semantic vector retrieval (ChromaDB / pgvector) over enterprise data catalogs.
* **Value:** Real-world enterprise databases contain hundreds of tables. Rather than stuffing the entire DDL schema into the LLM context window, a vector index retrieves only the top-$k$ relevant tables and business metric definitions based on the user's inquiry.

### 3. Causal Inference & Automated Root-Cause Engine (Beyond Correlation)

* **Goal:** Integrate causal inference libraries (such as Microsoft `DoWhy` or `EconML`).
* **Value:** When an anomaly is detected ($\vert{}Z\vert{} > 2$), the copilot automatically calculates counterfactual estimates to determine *why* it occurred (e.g., separating seasonal variation from machine mechanical failure).

### 4. Continuous Operational Monitoring & Webhook Alerting

* **Goal:** Deploy background scheduled workers (Celery / Apache Airflow) that run parameterized health-check queries periodically.
* **Value:** Proactively pings PagerDuty, Slack, or Microsoft Teams when metric bounds cross statistical control limits, accompanied by an executive diagnostic memo.

### 5. Multi-Variate Time-Series Forecasting (Prophet / NeuralProphet Integration)

* **Goal:** Overlay forward-looking predictive confidence intervals onto historical anomaly plots.
* **Value:** Allows supply chain and manufacturing teams to move from reactive mitigation to predictive capacity planning.
