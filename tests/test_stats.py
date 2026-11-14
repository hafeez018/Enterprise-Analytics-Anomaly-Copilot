import numpy as np
import pandas as pd
import pytest
from core.stats_engine import StatisticalAnalyzer


def test_standard_zscore_detects_outlier():
    # Setup data with a clear outlier
    df = pd.DataFrame({
        "date": ["2026-09-01", "2026-09-02", "2026-09-03", "2026-09-04", "2026-09-05", "2026-09-06"],
        "checkouts": [100, 102, 98, 101, 99, 10]  # Drop to 10 is an anomaly
    })
    
    result = StatisticalAnalyzer.detect_anomalies_zscore(df, metric_col="checkouts", threshold=2.0)
    
    assert "z_score" in result.columns
    assert "is_anomaly" in result.columns
    assert result.loc[5, "is_anomaly"] == True
    assert result.loc[0, "is_anomaly"] == False


def test_modified_zscore_mad_resistant_to_extreme_outliers():
    # Extreme outlier that would inflate standard deviation in standard Z-score
    df = pd.DataFrame({
        "checkouts": [50, 52, 49, 51, 50, 5000, 48, 51, 50, 52]
    })
    
    result = StatisticalAnalyzer.detect_anomalies_mad(df, metric_col="checkouts", threshold=3.5)
    
    assert "modified_z_score" in result.columns
    # The extreme outlier must be caught
    assert result.loc[5, "is_anomaly"] == True
    # The normal points around 50 should not be falsely flagged
    assert result.loc[0, "is_anomaly"] == False


def test_mad_handles_zero_variance_safely():
    # If all values are identical, MAD calculation must not throw ZeroDivisionError
    df = pd.DataFrame({"checkouts": [100, 100, 100, 100, 100]})
    result = StatisticalAnalyzer.detect_anomalies_mad(df, metric_col="checkouts", threshold=3.5)
    
    assert result["modified_z_score"].sum() == 0.0
    assert result["is_anomaly"].sum() == 0


def test_two_proportion_z_test_detects_significant_drop():
    # Baseline: 50% conversion (250/500). Experiment: 15% conversion (75/500)
    results = StatisticalAnalyzer.two_proportion_z_test(
        count1=250, nobs1=500,
        count2=75,  nobs2=500,
        alpha=0.05
    )
    
    assert results["is_significant"] == True
    assert results["p_value"] < 0.001
    assert results["relative_lift_pct"] == -70.0


def test_two_proportion_z_test_handles_insignificant_noise():
    # Minimal difference that should NOT trigger significance
    results = StatisticalAnalyzer.two_proportion_z_test(
        count1=100, nobs1=1000,
        count2=98,  nobs2=1000,
        alpha=0.05
    )
    
    assert results["is_significant"] == False
    assert results["p_value"] > 0.05