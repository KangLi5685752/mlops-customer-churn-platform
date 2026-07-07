"""Data loading and summary helpers for the local Streamlit dashboard."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

MONITORING_FEATURE_COLUMNS = [
    "tenure",
    "MonthlyCharges",
    "TotalCharges",
    "Contract",
    "InternetService",
    "PaymentMethod",
]
PREDICTION_LOG_COLUMNS = [
    "timestamp_utc",
    "request_id",
    "model_artifact_path",
    "churn_probability",
    "churn_prediction",
    "risk_label",
    "monitoring_features",
]
RISK_LABEL_ORDER = ["low", "medium", "high"]


def empty_prediction_logs_dataframe() -> pd.DataFrame:
    """Return an empty prediction log DataFrame with expected columns."""
    return pd.DataFrame(columns=PREDICTION_LOG_COLUMNS + MONITORING_FEATURE_COLUMNS)


def flatten_monitoring_features(df: pd.DataFrame) -> pd.DataFrame:
    """Flatten nested monitoring_features dictionaries into top-level columns."""
    if df.empty:
        return empty_prediction_logs_dataframe()

    flattened_df = df.copy()
    if "monitoring_features" not in flattened_df.columns:
        for feature in MONITORING_FEATURE_COLUMNS:
            if feature not in flattened_df.columns:
                flattened_df[feature] = None
        return flattened_df

    feature_df = pd.json_normalize(flattened_df["monitoring_features"].fillna({}))
    for feature in MONITORING_FEATURE_COLUMNS:
        if feature not in feature_df.columns:
            feature_df[feature] = None

    flattened_df = flattened_df.drop(columns=["monitoring_features"]).reset_index(drop=True)
    flattened_df = pd.concat(
        [flattened_df, feature_df[MONITORING_FEATURE_COLUMNS].reset_index(drop=True)],
        axis=1,
    )

    for feature in ["tenure", "MonthlyCharges", "TotalCharges", "churn_probability"]:
        if feature in flattened_df.columns:
            flattened_df[feature] = pd.to_numeric(flattened_df[feature], errors="coerce")

    return flattened_df


def load_prediction_logs(log_path: Path) -> pd.DataFrame:
    """Load local JSONL prediction logs into a flattened DataFrame."""
    if not log_path.exists():
        return empty_prediction_logs_dataframe()

    records: list[dict[str, Any]] = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict):
            records.append(record)

    if not records:
        return empty_prediction_logs_dataframe()

    return flatten_monitoring_features(pd.DataFrame(records))


def load_drift_results(path: Path) -> dict[str, Any]:
    """Load drift detection results from JSON, returning an empty dict if unavailable."""
    if not path.exists():
        return {}

    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

    return result if isinstance(result, dict) else {}


def prepare_risk_label_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare risk-label counts in stable low/medium/high order."""
    if df.empty or "risk_label" not in df.columns:
        counts = pd.Series(0, index=RISK_LABEL_ORDER)
    else:
        counts = df["risk_label"].value_counts().reindex(RISK_LABEL_ORDER, fill_value=0)

    return counts.rename_axis("risk_label").reset_index(name="count")


def summarise_prediction_logs(df: pd.DataFrame) -> dict[str, Any]:
    """Compute overview metrics for prediction logs."""
    total_events = int(len(df))
    if total_events == 0:
        return {
            "total_prediction_events": 0,
            "latest_prediction_timestamp": None,
            "average_churn_probability": None,
            "high_risk_percentage": 0.0,
            "risk_label_counts": {label: 0 for label in RISK_LABEL_ORDER},
        }

    risk_counts_df = prepare_risk_label_counts(df)
    risk_label_counts = dict(zip(risk_counts_df["risk_label"], risk_counts_df["count"]))
    high_count = int(risk_label_counts.get("high", 0))

    latest_timestamp = None
    if "timestamp_utc" in df.columns:
        latest_timestamp = df["timestamp_utc"].dropna().max()

    average_probability = None
    if "churn_probability" in df.columns:
        average_probability = float(pd.to_numeric(df["churn_probability"], errors="coerce").mean())

    return {
        "total_prediction_events": total_events,
        "latest_prediction_timestamp": latest_timestamp,
        "average_churn_probability": average_probability,
        "high_risk_percentage": high_count / total_events * 100,
        "risk_label_counts": risk_label_counts,
    }
