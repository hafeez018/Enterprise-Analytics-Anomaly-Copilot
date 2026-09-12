import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import gridspec


class ExecutiveReportVisualizer:
    """Generates multi-view enterprise visualization suites for executive dossiers."""

    # Modern dark palette
    BG_COLOR = "#0b0f19"
    SURFACE_COLOR = "#111827"
    TEXT_PRIMARY = "#f8fafc"
    TEXT_MUTED = "#94a3b8"
    GRID_COLOR = "#1e293b"
    ACCENT_CYAN = "#38bdf8"
    ACCENT_EMERALD = "#10b981"
    ALERT_RED = "#f43f5e"
    CHART_PALETTE = ["#38bdf8", "#818cf8", "#c084fc", "#34d399", "#fbbf24", "#f43f5e"]

    @classmethod
    def generate_dossier_visuals(
        cls, df: pd.DataFrame, x_date: str, y_metric: str, threshold_label: str
    ) -> plt.Figure:
        """
        Creates a synchronized 2-row multi-chart layout:
        Top Row: Primary Time-Series with Rolling Trend and Anomaly Markers.
        Bottom Left: Categorical or Quartile Distribution (Donut).
        Bottom Right: Metric Dispersion Density (Histogram + Outlier boundary).
        """
        fig = plt.figure(figsize=(14, 8.5), facecolor=cls.BG_COLOR)
        gs = gridspec.GridSpec(2, 2, height_ratios=[1.3, 1.0], hspace=0.35, wspace=0.25)

        # -------------------------------------------------------------
        # PANEL 1: Primary Time-Series Anomaly Trendline (Full Width)
        # -------------------------------------------------------------
        ax_main = fig.add_subplot(gs[0, :])
        ax_main.set_facecolor(cls.SURFACE_COLOR)

        x_vals = pd.to_datetime(df[x_date]) if "date" in x_date.lower() else df[x_date]
        y_vals = df[y_metric].to_numpy()

        # Primary baseline path
        ax_main.plot(
            x_vals,
            y_vals,
            color=cls.ACCENT_CYAN,
            linewidth=2.2,
            label=f"{y_metric} (Observed)",
            zorder=3,
        )
        ax_main.fill_between(
            x_vals, y_vals, color=cls.ACCENT_CYAN, alpha=0.08, zorder=2
        )

        # Flag Anomalies
        if "is_anomaly" in df.columns:
            anomalies = df[df["is_anomaly"]]
            if not anomalies.empty:
                x_anom = (
                    pd.to_datetime(anomalies[x_date])
                    if "date" in x_date.lower()
                    else anomalies[x_date]
                )
                ax_main.scatter(
                    x_anom,
                    anomalies[y_metric],
                    color=cls.ALERT_RED,
                    s=110,
                    edgecolor="#ffffff",
                    linewidth=1.5,
                    label=f"Statistical Anomaly ({threshold_label})",
                    zorder=5,
                )

        ax_main.set_title(
            f"Primary Metric Trajectory: {y_metric} over Time",
            color=cls.TEXT_PRIMARY,
            fontsize=13,
            fontweight="bold",
            pad=12,
        )
        ax_main.tick_params(colors=cls.TEXT_MUTED, labelsize=9)
        ax_main.grid(True, linestyle="--", color=cls.GRID_COLOR, alpha=0.7)
        for spine in ax_main.spines.values():
            spine.set_color(cls.GRID_COLOR)
        ax_main.legend(
            facecolor=cls.SURFACE_COLOR,
            edgecolor=cls.GRID_COLOR,
            labelcolor=cls.TEXT_PRIMARY,
            loc="upper left",
        )

        # -------------------------------------------------------------
        # PANEL 2: Distribution Breakdown (Donut Chart)
        # -------------------------------------------------------------
        ax_donut = fig.add_subplot(gs[1, 0])
        ax_donut.set_facecolor(cls.SURFACE_COLOR)

        # Detect categorical column if present, otherwise segment metric quartiles
        cat_cols = df.select_dtypes(include=["object", "category"]).columns
        cat_cols = [c for c in cat_cols if c != x_date]

        if len(cat_cols) > 0:
            top_cat = cat_cols[0]
            cat_summary = df.groupby(top_cat)[y_metric].sum().head(5)
            labels = cat_summary.index.astype(str)
            values = cat_summary.values
            donut_title = f"Volume Contribution by {top_cat.title()}"
        else:
            # Quartile bins
            labels = ["Q1 (Low)", "Q2 (Mid-Low)", "Q3 (Mid-High)", "Q4 (Peak)"]
            values = (
                pd.qcut(df[y_metric], q=4, labels=False, duplicates="drop")
                .value_counts()
                .sort_index()
                .values
            )
            donut_title = "Distribution Spread (Quartiles)"

        wedges, texts, autotexts = ax_donut.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            colors=cls.CHART_PALETTE[: len(values)],
            startangle=140,
            pctdistance=0.75,
            textprops={"color": cls.TEXT_PRIMARY, "fontsize": 8.5},
            wedgeprops={"edgecolor": cls.BG_COLOR, "linewidth": 2},
        )
        for at in autotexts:
            at.set_color("#000000")
            at.set_fontweight("bold")

        # Create hole for Donut
        centre_circle = plt.Circle((0, 0), 0.52, fc=cls.SURFACE_COLOR)
        ax_donut.add_artist(centre_circle)
        ax_donut.set_title(
            donut_title, color=cls.TEXT_PRIMARY, fontsize=11, fontweight="bold", pad=10
        )

        # -------------------------------------------------------------
        # PANEL 3: Metric Density & Outlier Dispersion
        # -------------------------------------------------------------
        ax_hist = fig.add_subplot(gs[1, 1])
        ax_hist.set_facecolor(cls.SURFACE_COLOR)

        counts, bins, patches = ax_hist.hist(
            y_vals, bins=15, color=cls.ACCENT_CYAN, alpha=0.75, edgecolor=cls.BG_COLOR
        )
        median_val = np.nanmedian(y_vals)
        ax_hist.axvline(
            median_val,
            color=cls.ACCENT_EMERALD,
            linestyle="--",
            linewidth=1.8,
            label=f"Median ({median_val:.1f})",
        )

        ax_hist.set_title(
            "Value Frequency & Dispersion",
            color=cls.TEXT_PRIMARY,
            fontsize=11,
            fontweight="bold",
            pad=10,
        )
        ax_hist.tick_params(colors=cls.TEXT_MUTED, labelsize=9)
        ax_hist.grid(True, linestyle="--", color=cls.GRID_COLOR, alpha=0.7)
        for spine in ax_hist.spines.values():
            spine.set_color(cls.GRID_COLOR)
        ax_hist.legend(
            facecolor=cls.SURFACE_COLOR,
            edgecolor=cls.GRID_COLOR,
            labelcolor=cls.TEXT_PRIMARY,
            loc="upper right",
        )

        return fig


def render_neural_dag(active_step: int = 0, error_step: int = None) -> str:
    """Renders the animated SVG pipeline reflecting real-time execution state without Markdown indentation traps."""
    steps = [
        {"id": 1, "name": "1. NL Ingestion", "color": "#38bdf8", "x": 10},
        {"id": 2, "name": "2. Gemini LLM", "color": "#818cf8", "x": 230},
        {"id": 3, "name": "3. AST Guard", "color": "#f43f5e", "x": 460},
        {"id": 4, "name": "4. RO Sandbox", "color": "#10b981", "x": 680},
        {"id": 5, "name": "5. Dossier", "color": "#c084fc", "x": 890},
    ]

    nodes_svg = []
    for s in steps:
        s_id = s["id"]
        x = s["x"]

        if error_step == s_id:
            stroke = "#f43f5e"
            fill = "rgba(244, 63, 94, 0.2)"
            text_color = "#fca5a5"
            status_badge = "✕ Error"
            css_class = "node-error"
        elif active_step == s_id:
            stroke = s["color"]
            fill = "rgba(15, 23, 42, 0.95)"
            text_color = "#ffffff"
            status_badge = "⚡ Processing"
            css_class = "node-active"
        elif active_step > s_id or active_step == 6:
            stroke = "#10b981"
            fill = "rgba(16, 185, 129, 0.12)"
            text_color = "#a7f3d0"
            status_badge = "✓ Verified"
            css_class = "node-complete"
        else:
            stroke = "#334155"
            fill = "rgba(15, 23, 42, 0.5)"
            text_color = "#64748b"
            status_badge = "Standby"
            css_class = "node-idle"

        # Formatted without leading 4-space indents to bypass markdown code formatting
        node_str = (
            f'<g transform="translate({x}, 12)" class="{css_class}">'
            f'<rect width="125" height="46" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.8"/>'
            f'<text x="62" y="22" fill="{text_color}" font-size="11" font-weight="700" text-anchor="middle">{s["name"]}</text>'
            f'<text x="62" y="37" fill="{stroke}" font-size="8.5" font-weight="600" text-anchor="middle">{status_badge}</text>'
            f"</g>"
        )
        nodes_svg.append(node_str)

    flow_class = "packet-flow" if (0 < active_step < 6) else ""
    connector_stroke = "#38bdf8" if active_step > 0 else "#334155"
    step_indicator = (
        "● Pipeline Complete"
        if active_step == 6
        else f"● Step {active_step}/5 Active"
        if active_step > 0
        else "○ System Standby"
    )
    indicator_color = (
        "#10b981" if active_step == 6 else "#38bdf8" if active_step > 0 else "#64748b"
    )

    # Unindented HTML template to prevent CommonMark pre/code wrapping
    return (
        f"<style>"
        f"@keyframes pulseGlow {{"
        f"0% {{ filter: drop-shadow(0 0 2px {steps[min(max(active_step - 1, 0), 4)]['color']}); }}"
        f"50% {{ filter: drop-shadow(0 0 12px {steps[min(max(active_step - 1, 0), 4)]['color']}); }}"
        f"100% {{ filter: drop-shadow(0 0 2px {steps[min(max(active_step - 1, 0), 4)]['color']}); }}"
        f"}}"
        f"@keyframes dataFlow {{"
        f"from {{ stroke-dashoffset: 24; }}"
        f"to {{ stroke-dashoffset: 0; }}"
        f"}}"
        f".node-active {{ animation: pulseGlow 1.4s ease-in-out infinite; }}"
        f".packet-flow {{ stroke-dasharray: 6 6; animation: dataFlow 0.8s linear infinite; }}"
        f"</style>"
        f'<div style="background: #0b0f19; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px; padding: 0.9rem 1.25rem; margin-bottom: 1.25rem;">'
        f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">'
        f'<span style="font-size: 0.72rem; font-weight: 700; letter-spacing: 0.1em; color: #94a3b8; text-transform: uppercase;">'
        f"⚡ Neural Pipeline State Machine"
        f"</span>"
        f'<span style="font-size: 0.75rem; color: {indicator_color}; font-weight: 600;">'
        f"{step_indicator}"
        f"</span>"
        f"</div>"
        f'<svg width="100%" height="72" viewBox="0 0 1025 72" fill="none" xmlns="http://www.w3.org/2000/svg">'
        f'<path d="M 135 35 H 230 M 355 35 H 460 M 585 35 H 680 M 805 35 H 890" stroke="#1e293b" stroke-width="2.5"/>'
        f'<path d="M 135 35 H 230 M 355 35 H 460 M 585 35 H 680 M 805 35 H 890" stroke="{connector_stroke}" stroke-width="2" class="{flow_class}"/>'
        f"{''.join(nodes_svg)}"
        f"</svg>"
        f"</div>"
    )
