"""Local Streamlit monitoring dashboard for prediction logs and drift reports."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from src.monitoring.dashboard_data import (
    MONITORING_FEATURE_COLUMNS,
    load_drift_results,
    load_prediction_logs,
    prepare_risk_label_counts,
    summarise_prediction_logs,
)
from src.utils.paths import PROJECT_ROOT

PREDICTION_LOG_PATH = PROJECT_ROOT / "logs" / "predictions.jsonl"
DRIFT_RESULTS_PATH = PROJECT_ROOT / "reports" / "drift_detection_results.json"


def format_float(value: float | None, digits: int = 3) -> str:
    """Format optional float values for dashboard metrics."""
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.{digits}f}"


def build_probability_bins(df: pd.DataFrame) -> pd.DataFrame:
    """Build a binned churn-probability distribution for Streamlit charting."""
    if df.empty or "churn_probability" not in df.columns:
        return pd.DataFrame(columns=["probability_bin", "count"])

    bins = pd.cut(
        df["churn_probability"],
        bins=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
        include_lowest=True,
    )
    return bins.value_counts().sort_index().rename_axis("probability_bin").reset_index(name="count")


def numerical_feature_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Build summary stats for numerical monitoring features."""
    numerical_features = ["tenure", "MonthlyCharges", "TotalCharges"]
    rows: list[dict[str, Any]] = []
    for feature in numerical_features:
        if feature not in df.columns:
            continue
        series = pd.to_numeric(df[feature], errors="coerce")
        rows.append(
            {
                "feature": feature,
                "mean": series.mean(),
                "min": series.min(),
                "max": series.max(),
            }
        )
    return pd.DataFrame(rows)


def categorical_feature_counts(df: pd.DataFrame, feature: str) -> pd.DataFrame:
    """Build value counts for one categorical monitoring feature."""
    if df.empty or feature not in df.columns:
        return pd.DataFrame(columns=[feature, "count"])

    return df[feature].value_counts().rename_axis(feature).reset_index(name="count")


def drift_table(drift_results: dict[str, Any], drift_key: str) -> pd.DataFrame:
    """Convert drift result dictionaries into display tables."""
    rows: list[dict[str, Any]] = []
    for feature, result in drift_results.get(drift_key, {}).items():
        row = {"feature": feature, **result}
        rows.append(row)
    return pd.DataFrame(rows)


st.set_page_config(
    page_title="MLOps Churn Monitoring",
    layout="wide",
)

st.title("MLOps Customer Churn Monitoring Dashboard")
st.caption(
    "Local prototype dashboard for prediction logs and simulated drift detection. "
    "Not production monitoring."
)

prediction_df = load_prediction_logs(PREDICTION_LOG_PATH)
drift_results = load_drift_results(DRIFT_RESULTS_PATH)

st.header("Prediction Log Overview")
if prediction_df.empty:
    st.warning(
        "Prediction logs were not found. Generate prediction traffic first with "
        "`python -m scripts.generate_sample_prediction_traffic --n 30`."
    )
else:
    summary = summarise_prediction_logs(prediction_df)
    metric_columns = st.columns(4)
    metric_columns[0].metric("Total prediction events", summary["total_prediction_events"])
    metric_columns[1].metric(
        "Latest prediction timestamp",
        summary["latest_prediction_timestamp"] or "n/a",
    )
    metric_columns[2].metric(
        "Average churn probability",
        format_float(summary["average_churn_probability"]),
    )
    metric_columns[3].metric(
        "High-risk predictions",
        f"{summary['high_risk_percentage']:.1f}%",
    )

    risk_counts = prepare_risk_label_counts(prediction_df)
    st.subheader("Risk Label Counts")
    st.dataframe(risk_counts, use_container_width=True, hide_index=True)

    st.subheader("Risk Label Distribution")
    st.bar_chart(risk_counts.set_index("risk_label"))

    st.subheader("Churn Probability Distribution")
    probability_bins = build_probability_bins(prediction_df)
    if probability_bins.empty:
        st.info("No churn probability values are available.")
    else:
        probability_bins["probability_bin"] = probability_bins["probability_bin"].astype(str)
        st.bar_chart(probability_bins.set_index("probability_bin"))

    st.header("Monitoring Feature Summaries")
    st.subheader("Numerical Features")
    st.dataframe(numerical_feature_summary(prediction_df), use_container_width=True, hide_index=True)

    st.subheader("Categorical Features")
    for feature in ["Contract", "InternetService", "PaymentMethod"]:
        st.markdown(f"**{feature}**")
        st.dataframe(
            categorical_feature_counts(prediction_df, feature),
            use_container_width=True,
            hide_index=True,
        )

st.header("Drift Detection Overview")
if not drift_results:
    st.warning(
        "Drift detection results were not found. Run "
        "`python -m scripts.run_simulated_drift_detection`."
    )
else:
    drift_columns = st.columns(3)
    drift_columns[0].metric(
        "Overall drift detected",
        str(drift_results.get("overall_drift_detected", "n/a")),
    )
    drift_columns[1].metric(
        "Reference records",
        drift_results.get("reference_record_count", "n/a"),
    )
    drift_columns[2].metric(
        "Simulated current records",
        drift_results.get("current_record_count", "n/a"),
    )
    st.info(drift_results.get("simulation_note", "Current batch is simulated."))

    st.subheader("Numerical Drift Table")
    st.dataframe(
        drift_table(drift_results, "numerical_drift"),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Categorical Drift Table")
    st.dataframe(
        drift_table(drift_results, "categorical_drift"),
        use_container_width=True,
        hide_index=True,
    )

st.header("Limitations")
st.markdown(
    "\n".join(
        [
            "- Prediction traffic is synthetic local sample traffic.",
            "- Drift current batch is simulated.",
            "- No ground-truth labels are used.",
            "- Thresholds are demonstration thresholds.",
            "- This is not production observability.",
        ]
    )
)
