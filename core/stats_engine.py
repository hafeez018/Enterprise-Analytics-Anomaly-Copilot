import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from typing import Any


class StatisticalAnalyzer:
    """
    Mathematical and statistical analysis engine for product metrics.
    Includes parametric (Z-score) and non-parametric (Modified Z-score / MAD)
    anomaly detection, hypothesis testing, and time-series plotting.
    """

    @staticmethod
    def detect_anomalies(
        df: pd.DataFrame, metric_col: str, threshold: float = 3.5
    ) -> pd.DataFrame:
        """
        Default backwards-compatible entry point.
        Routes to robust Modified Z-Score (MAD) anomaly detection.
        """
        return StatisticalAnalyzer.detect_anomalies_mad(
            df, metric_col=metric_col, threshold=threshold
        )

    @staticmethod
    def detect_anomalies_zscore(
        df: pd.DataFrame, metric_col: str, threshold: float = 2.0
    ) -> pd.DataFrame:
        """
        Parametric anomaly detection using standard Z-score:
            Z = (X - μ) / σ
        Best suited for roughly normal distributions.
        """
        result_df = df.copy()
        if metric_col not in result_df.columns or len(result_df) < 5:
            result_df["z_score"] = 0.0
            result_df["is_anomaly"] = False
            return result_df

        values = result_df[metric_col].to_numpy(dtype=float)
        mean = np.nanmean(values)
        std = np.nanstd(values)

        if std == 0 or np.isnan(std):
            result_df["z_score"] = 0.0
            result_df["is_anomaly"] = False
        else:
            result_df["z_score"] = (values - mean) / std
            result_df["is_anomaly"] = np.abs(result_df["z_score"]) > threshold

        return result_df

    @staticmethod
    def detect_anomalies_mad(
        df: pd.DataFrame, metric_col: str, threshold: float = 3.5
    ) -> pd.DataFrame:
        """
        Robust non-parametric outlier detection using Modified Z-Score (Boris Iglewicz & David Hoaglin):
            MAD = median(|X_i - median(X)|)
            M_i = (0.6745 * (X_i - median(X))) / MAD

        Resistant to extreme outliers and skewed distributions. Flagged when |M_i| > threshold (default 3.5).
        """
        result_df = df.copy()
        if metric_col not in result_df.columns or len(result_df) < 5:
            result_df["modified_z_score"] = 0.0
            result_df["is_anomaly"] = False
            return result_df

        values = result_df[metric_col].to_numpy(dtype=float)
        median = np.nanmedian(values)
        abs_deviations = np.abs(values - median)
        mad = np.nanmedian(abs_deviations)

        # Fallback if MAD is 0 (occurs when > 50% of the sample values are identical)
        if mad == 0:
            mean_ad = np.nanmean(abs_deviations)
            if mean_ad == 0:
                result_df["modified_z_score"] = 0.0
                result_df["is_anomaly"] = False
                return result_df
            # Approximate scale using mean absolute deviation
            scale = 1.2533 * mean_ad
        else:
            scale = mad

        result_df["modified_z_score"] = (0.6745 * (values - median)) / scale
        result_df["is_anomaly"] = np.abs(result_df["modified_z_score"]) > threshold

        return result_df

    @staticmethod
    def two_proportion_z_test(
        count1: int, nobs1: int, count2: int, nobs2: int, alpha: float = 0.05
    ) -> dict[str, Any]:
        """
        Performs a two-sided, two-proportion hypothesis test (e.g., comparing baseline
        vs. post-release checkout conversion rates).

            H0: p1 - p2 = 0
            H1: p1 - p2 != 0

        Formulas:
            p1 = count1 / nobs1,  p2 = count2 / nobs2
            p_pool = (count1 + count2) / (nobs1 + nobs2)
            SE = sqrt(p_pool * (1 - p_pool) * (1/nobs1 + 1/nobs2))
            Z = (p1 - p2) / SE
        """
        if nobs1 <= 0 or nobs2 <= 0:
            raise ValueError(
                "Observation counts (nobs1, nobs2) must be positive integers."
            )

        p1 = count1 / nobs1
        p2 = count2 / nobs2
        p_pool = (count1 + count2) / (nobs1 + nobs2)

        variance = p_pool * (1 - p_pool) * ((1 / nobs1) + (1 / nobs2))
        se = np.sqrt(variance)

        if se == 0:
            z_stat = 0.0
            p_value = 1.0
        else:
            z_stat = (p1 - p2) / se
            # Two-tailed p-value from standard normal distribution
            p_value = float(2 * stats.norm.sf(np.abs(z_stat)))

        relative_lift = ((p2 - p1) / p1 * 100) if p1 > 0 else 0.0

        return {
            "baseline_conversion": round(p1, 4),
            "current_conversion": round(p2, 4),
            "absolute_difference": round(p2 - p1, 4),
            "relative_lift_pct": round(relative_lift, 2),
            "pooled_proportion": round(p_pool, 4),
            "standard_error": round(se, 6),
            "z_statistic": round(z_stat, 4),
            "p_value": round(p_value, 6),
            "alpha": alpha,
            "is_significant": bool(p_value < alpha),
        }

    @staticmethod
    def plot_metric(
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str,
        score_col: str | None = None,
    ) -> plt.Figure:
        """
        Renders a Seaborn time-series line plot with anomalies highlighted in red.
        """
        fig, ax = plt.subplots(figsize=(10, 4.5))
        sns.set_theme(style="whitegrid")

        # Plot primary trendline
        sns.lineplot(
            data=df,
            x=x_col,
            y=y_col,
            ax=ax,
            color="#1f77b4",
            marker="o",
            linewidth=2,
            label=y_col,
        )

        # Highlight detected anomalies
        if "is_anomaly" in df.columns:
            anomalies = df[df["is_anomaly"]]
            if not anomalies.empty:
                label = f"Anomaly ({score_col})" if score_col else "Anomaly"
                ax.scatter(
                    anomalies[x_col],
                    anomalies[y_col],
                    color="#d62728",
                    s=90,
                    zorder=5,
                    label=label,
                )

        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
        ax.set_xlabel(x_col, fontweight="semibold")
        ax.set_ylabel(y_col, fontweight="semibold")
        plt.xticks(rotation=45)
        plt.tight_layout()
        ax.legend(loc="upper left")
        return fig
