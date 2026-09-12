import os
import time
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
from core.database import DatabaseManager
from core.gemini_agent import GeminiAnalyticsAgent
from core.report_engine import ExecutiveReportVisualizer, render_neural_dag
from core.security import SQLSecurityError
from core.stats_engine import StatisticalAnalyzer

# --- Page Setup ---
st.set_page_config(
    page_title="Autonomous Analytics Copilot Enterprise",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Enterprise CSS Theme ---
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* 2. REMOVE STREAMLIT INPUT INSTRUCTIONS (Press Enter to continue) */
    [data-testid="InputInstructions"] {
        display: none !important;
    }

    /* Hero Command Card */
    .command-header {
        padding: 1.5rem 2rem;
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.95) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 16px;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5);
    }
    .badge-pipeline {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #38bdf8;
        background: rgba(56, 189, 248, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 3px 10px;
        border-radius: 9999px;
    }
    .title-text {
        font-size: 1.8rem;
        font-weight: 700;
        color: #f8fafc;
        margin: 0.4rem 0 0.2rem 0;
    }
    .subtitle-text {
        font-size: 0.9rem;
        color: #94a3b8;
    }

    /* Neural Pipeline Card */
    .dag-container {
        background: #0b0f19;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1.5rem;
    }

    /* Sidebar Luxury Enhancements */
    .sidebar-card {
        background: rgba(17, 24, 39, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .status-live {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.78rem;
        color: #10b981;
        font-weight: 600;
    }

    /* Executive Dossier Card */
    .dossier-card {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.9) 0%, rgba(11, 15, 25, 0.95) 100%);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 16px;
        padding: 1.75rem 2rem;
        margin-top: 1.5rem;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.6);
    }
    .dossier-tag {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #10b981;
        background: rgba(16, 185, 129, 0.12);
        padding: 3px 8px;
        border-radius: 6px;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    /* Dropzone Empty State */
    .empty-state-card {
        text-align: center;
        padding: 3rem 2rem;
        background: rgba(15, 23, 42, 0.4);
        border: 2px dashed rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        margin-top: 1.5rem;
    }
</style>
""",
    unsafe_allow_html=True,
)


# --- Service Registry ---
@st.cache_resource
def get_db_manager():
    return DatabaseManager(db_path="data/product_metrics.db")


db = get_db_manager()
analyzer = StatisticalAnalyzer()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# --- 5. REDESIGNED ENTERPRISE SIDEBAR ---
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-card">
            <span class="status-live">● TELEMETRY ONLINE</span>
            <div style="font-size: 0.9rem; font-weight: 700; color: #f8fafc; margin-top: 4px;">Zero-Trust Control Plane</div>
            <div style="font-size: 0.75rem; color: #94a3b8;">Runtime: Python 3.10+ | AST Guard Active</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("### 🗄️ Enterprise Database Hub")
    data_source = st.radio(
        "Ingestion Channel:",
        ["Synthetic Multi-Channel Benchmark", "Custom Enterprise SQLite (.db)"],
        label_visibility="collapsed",
    )

    custom_db_attached = False

    if data_source == "Custom Enterprise SQLite (.db)":
        uploaded_db = st.file_uploader(
            "Attach SQLite binary (.db, .sqlite)", type=["db", "sqlite", "sqlite3"]
        )
        if uploaded_db is not None:
            os.makedirs("data/custom", exist_ok=True)
            custom_path = os.path.join("data/custom", uploaded_db.name)
            with open(custom_path, "wb") as f:
                f.write(uploaded_db.getbuffer())
            db.update_database(custom_path)
            custom_db_attached = True
            st.success(f"Attached: `{uploaded_db.name}`")
    else:
        if not os.path.exists("data/product_metrics.db"):
            st.warning("Benchmark DB not generated. Run `python data/setup_db.py`.")
        db.update_database("data/product_metrics.db")
        custom_db_attached = True
        st.caption("Active Source: `data/product_metrics.db` [Read-Only URI]")

    # Dynamic Catalog Inspector
    try:
        tables = db.get_table_names()
        with st.expander(
            f"📦 Active Schema Entities ({len(tables)} Tables)", expanded=False
        ):
            for t in tables:
                st.markdown(f"- `{t}`")
    except Exception:
        st.caption("Catalog query pending file attachment.")

    st.markdown("---")
    st.markdown("### 📐 Statistical Anomaly Model")
    anomaly_method = st.selectbox(
        "Algorithm",
        ["Modified Z-Score (Robust MAD)", "Standard Gaussian Z-Score"],
        help="MAD is resistant to outlier masking on skewed enterprise metrics.",
    )

    if "MAD" in anomaly_method:
        threshold = st.slider("Anomaly Threshold (|M_i|)", 2.0, 5.0, 3.5, 0.1)
    else:
        threshold = st.slider("Anomaly Threshold (|Z|)", 1.5, 3.5, 2.0, 0.1)

# --- 1. RESOLVE EMPTY SCREEN ON UPLOAD ---
# If custom mode selected but no file attached yet, render an informative dropzone placeholder
if data_source == "Custom Enterprise SQLite (.db)" and not custom_db_attached:
    st.markdown(
        """
    <div class="command-header">
        <div class="badge-pipeline">Awaiting Ingestion</div>
        <div class="title-text">Connect Enterprise Database</div>
        <div class="subtitle-text">Attach an operational SQLite database via the sidebar to run zero-hallucination conversational diagnostics.</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <div class="empty-state-card">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📂</div>
        <div style="font-size: 1.2rem; font-weight: 700; color: #f8fafc;">No Database File Detected</div>
        <div style="font-size: 0.9rem; color: #94a3b8; max-width: 500px; margin: 0.5rem auto 1.5rem auto;">
            Use the <b>Enterprise Database Hub</b> in the left sidebar to upload your <code>.db</code>, <code>.sqlite</code>, or <code>.sqlite3</code> file. The engine will dynamically parse table catalogs and build the semantic context automatically.
        </div>
        <div style="display: inline-flex; gap: 10px;">
            <span style="font-size: 0.8rem; background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56,189,248,0.25); color: #38bdf8; padding: 4px 12px; border-radius: 6px;">Zero Data Hallucination</span>
            <span style="font-size: 0.8rem; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16,185,129,0.25); color: #10b981; padding: 4px 12px; border-radius: 6px;">OS Read-Only Lock</span>
            <span style="font-size: 0.8rem; background: rgba(192, 132, 252, 0.1); border: 1px solid rgba(192,132,252,0.25); color: #c084fc; padding: 4px 12px; border-radius: 6px;">AST Injection Shield</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.stop()

# --- HERO COMMAND CARD ---
st.markdown(
    """
<div class="command-header">
    <div class="badge-pipeline">Autonomous Cognitive System</div>
    <div class="title-text">Enterprise Analytics & Anomaly Copilot</div>
    <div class="subtitle-text">Zero-Hallucination Query Compilation • AST Security Sandbox • Self-Healing Reflexion • Multimodal Executive Reporting</div>
</div>
""",
    unsafe_allow_html=True,
)

dag_placeholder = st.empty()

# Question Input Section
templates = [
    "Select an executive question template...",
    "What is the daily checkout count by device over the past 30 days?",
    "Show total revenue and count of orders grouped by user plan.",
    "Show the count of each event type by day over the last two weeks.",
    "What is the daily total order amount over time?",
]
selected_tpl = st.selectbox("Quick-start question templates:", templates)
query_val = (
    "" if selected_tpl == "Select an executive question template..." else selected_tpl
)
user_query = st.text_input(
    "Operational inquiry:",
    value=query_val,
    placeholder="e.g., What is the daily conversion rate on Android?",
)

submit_btn = st.button(
    "Execute Autonomous Cognitive Pipeline", type="primary", use_container_width=True
)

# --- 3. EXECUTION PIPELINE WITH SEQUENTIAL STEPPER ---
if submit_btn:
    if not GEMINI_API_KEY:
        st.error(
            "Missing Gemini API credentials. Ensure `GEMINI_API_KEY` is present in your `.env` file."
        )
        st.stop()

    if not user_query.strip():
        st.warning("Please provide a prompt or select a pre-configured template.")
        st.stop()

    agent = GeminiAnalyticsAgent(api_key=GEMINI_API_KEY)
    schema = db.get_schema()

    # Step-by-step progress tracking container
    with st.status(
        "Executing Cognitive Pipeline Sequence...", expanded=True
    ) as pipeline_status:
        dag_placeholder.markdown(
            render_neural_dag(active_step=1), unsafe_allow_html=True
        )
        st.write(
            "🔍 **Phase 1: Dynamic DDL Introspection** — Extracting active catalog and constraint graphs..."
        )
        time.sleep(0.3)

        dag_placeholder.markdown(
            render_neural_dag(active_step=2), unsafe_allow_html=True
        )
        st.write(
            "⚡ **Phase 2: Semantic SQL Compilation** — Translating natural language to SQLite dialect via Gemini..."
        )
        time.sleep(0.3)

        dag_placeholder.markdown(
            render_neural_dag(active_step=3), unsafe_allow_html=True
        )
        st.write(
            "🛡️ **Phase 3: AST Security & Injection Guard** — Scanning parse tree with `sqlglot` for mutations & stacked calls..."
        )
        time.sleep(0.3)

        dag_placeholder.markdown(
            render_neural_dag(active_step=4), unsafe_allow_html=True
        )
        st.write(
            "🔒 **Phase 4: Sandboxed Execution & Reflexion** — Executing query against immutable `mode=ro` SQLite URI..."
        )

        try:
            df, final_sql, logs = agent.execute_with_self_healing(
                user_question=user_query,
                schema=schema,
                db_path=db.db_path,
                max_retries=3,
            )
            dag_placeholder.markdown(
                render_neural_dag(active_step=5), unsafe_allow_html=True
            )
            st.write(
                "📐 **Phase 5: Statistical Inference Engine** — Computing robust non-parametric anomaly bounds (MAD)..."
            )
            time.sleep(0.3)

            dag_placeholder.markdown(
                render_neural_dag(active_step=6), unsafe_allow_html=True
            )
            st.write(
                "📊 **Phase 6: Multi-Modal Dossier Assembly** — Synthesizing multi-view visual suite and executive takeaways..."
            )
            time.sleep(0.3)

            pipeline_status.update(
                label="Cognitive Pipeline Complete: Zero Policy Violations",
                state="complete",
                expanded=False,
            )

        except SQLSecurityError as sec_err:
            pipeline_status.update(
                label="Security Guardrail Violation Detected",
                state="error",
                expanded=True,
            )
            st.error(f"🚫 AST Security Guardrail Rejection: {sec_err}")
            st.caption(
                "Execution halted before database interaction to protect storage integrity."
            )
            st.stop()
        except Exception as e:
            pipeline_status.update(
                label="Pipeline Execution Error", state="error", expanded=True
            )
            st.error(f"Execution Error: {e}")
            st.stop()

    # Self-Healing Trace Display
    if len(logs) > 1:
        st.warning(
            f"⚠️ Query required autonomous self-healing (Resolved on Attempt #{len(logs)})"
        )
        with st.expander("Inspect Autonomous Reflexion Trace", expanded=False):
            for entry in logs:
                if entry["status"] == "failed":
                    st.error(f"Attempt #{entry['attempt']} Error: {entry['error']}")
                    st.code(entry["sql"], language="sql")
                else:
                    st.success(f"Attempt #{entry['attempt']} Resolved:")
                    st.code(entry["sql"], language="sql")
    else:
        with st.expander("Verified AST-Sanitized SQL", expanded=False):
            st.code(final_sql, language="sql")

    if df.empty:
        st.warning("Query executed successfully, but returned zero matching records.")
        st.stop()

    # --- ROW 1: FULL WIDTH QUERY RESULT SET ---
    st.markdown("### 📋 Verified Query Records")
    st.dataframe(df, use_container_width=True, height=260)

    col_meta1, col_meta2 = st.columns([6, 1])
    with col_meta1:
        st.caption(
            f"Retrieved {len(df)} records. All arithmetic produced deterministically."
        )
    with col_meta2:
        st.download_button(
            "Export CSV",
            df.to_csv(index=False).encode("utf-8"),
            "query_results.csv",
            "text/csv",
            use_container_width=True,
        )

    # --- 4. EXECUTIVE DOSSIER (FLOATING MODERN REPORT WITH MULTI-MODAL CHARTS) ---
    num_cols = df.select_dtypes(
        include=["float64", "int64", "float32", "int32"]
    ).columns.tolist()
    date_cols = [
        c
        for c in df.columns
        if any(k in c.lower() for k in ["date", "time", "day", "month", "timestamp"])
    ]

    st.markdown(
        """
    <div class="dossier-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <span class="dossier-tag">Executive Intelligence Dossier</span>
            <span style="font-size: 0.8rem; color: #94a3b8;">Automated Root-Cause Synthesis</span>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Executive Metric Badges
    if len(num_cols) > 0:
        primary_metric = num_cols[0]
        metric_series = df[primary_metric].dropna()
        m_mean = metric_series.mean()
        m_max = metric_series.max()
        m_min = metric_series.min()

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Sample Volume", f"{len(df):,}")
        kpi2.metric(f"Mean ({primary_metric})", f"{m_mean:,.2f}")
        kpi3.metric("Peak Record", f"{m_max:,.2f}")
        kpi4.metric("Trough Record", f"{m_min:,.2f}")

    # Render Visual Suite if Temporal and Numeric Dimensions Exist
    if len(num_cols) > 0 and len(date_cols) > 0:
        y_val = num_cols[0]
        x_val = date_cols[0]
        df_sorted = df.sort_values(by=x_val).copy()

        if "MAD" in anomaly_method:
            df_analyzed = analyzer.detect_anomalies_mad(
                df_sorted, metric_col=y_val, threshold=threshold
            )
            score_tag = f"MAD |M_i| > {threshold}"
        else:
            df_analyzed = analyzer.detect_anomalies_zscore(
                df_sorted, metric_col=y_val, threshold=threshold
            )
            score_tag = f"StdDev |Z| > {threshold}"

        # Render the 3-panel multi-modal executive chart
        dossier_fig = ExecutiveReportVisualizer.generate_dossier_visuals(
            df=df_analyzed, x_date=x_val, y_metric=y_val, threshold_label=score_tag
        )
        st.pyplot(dossier_fig, use_container_width=True)

        anom_count = (
            df_analyzed["is_anomaly"].sum()
            if "is_anomaly" in df_analyzed.columns
            else 0
        )
        if anom_count > 0:
            st.error(
                f"🚨 Flagged {anom_count} statistically significant outlier(s) using {score_tag}."
            )
        else:
            st.success(
                "✅ Metric observations conform within expected mathematical bounds."
            )

    # Executive LLM Strategic Summary
    st.markdown("#### 📝 Diagnostic & Operational Brief")
    with st.spinner("Synthesizing executive briefing..."):
        summary_payload = {
            "query": user_query,
            "record_count": len(df),
            "descriptive_stats": df.describe(include="all").to_string(),
            "sample_head": df.head(5).to_dict(orient="records"),
        }
        briefing = agent.generate_executive_insights(user_query, str(summary_payload))
        st.markdown(briefing)

    st.markdown("</div>", unsafe_allow_html=True)
