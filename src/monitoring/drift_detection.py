"""Simulated local drift detection from prediction log events."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

NUMERICAL_FEATURES = [
    "tenure",
    "MonthlyCharges",
    "TotalCharges",
    "churn_probability",
]
CATEGORICAL_FEATURES = [
    "Contract",
    "InternetService",
    "PaymentMethod",
    "risk_label",
]
SIMULATION_NOTE = (
    "The current batch is simulated by applying deterministic feature shifts to "
    "local prediction logs. This is not real production drift monitoring."
)


def load_prediction_events(log_path: Path) -> list[dict[str, Any]]:
    """Load valid JSON prediction events from a JSONL log file."""
    if not log_path.exists():
        raise FileNotFoundError(f"Prediction log file not found: {log_path}")

    events: list[dict[str, Any]] = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            events.append(event)

    return events


def prediction_events_to_dataframe(events: list[dict[str, Any]]) -> pd.DataFrame:
    """Convert prediction log events into a monitoring DataFrame."""
    rows: list[dict[str, Any]] = []
    for event in events:
        monitoring_features = event.get("monitoring_features") or {}
        row = {feature: monitoring_features.get(feature) for feature in CATEGORICAL_FEATURES}
        row.update(
            {
                "tenure": monitoring_features.get("tenure"),
                "MonthlyCharges": monitoring_features.get("MonthlyCharges"),
                "TotalCharges": monitoring_features.get("TotalCharges"),
                "churn_probability": event.get("churn_probability"),
                "risk_label": event.get("risk_label"),
            }
        )
        rows.append(row)

    df = pd.DataFrame(rows)
    for feature in NUMERICAL_FEATURES:
        if feature in df.columns:
            df[feature] = pd.to_numeric(df[feature], errors="coerce")

    return df


def risk_label_from_probability(churn_probability: float) -> str:
    """Map churn probability to the same simple local risk labels used by the API."""
    if churn_probability >= 0.65:
        return "high"
    if churn_probability >= 0.35:
        return "medium"
    return "low"


def simulate_current_batch(
    reference_df: pd.DataFrame,
    random_seed: int = 42,
) -> pd.DataFrame:
    """Create a deterministic simulated current batch with shifted distributions."""
    current_df = reference_df.copy(deep=True)
    if current_df.empty:
        return current_df

    rng = np.random.default_rng(random_seed)
    row_count = len(current_df)
    majority_count = max(1, int(round(row_count * 0.7)))
    partial_count = max(1, int(round(row_count * 0.5)))
    majority_indices = rng.choice(current_df.index.to_numpy(), size=majority_count, replace=False)
    partial_indices = rng.choice(current_df.index.to_numpy(), size=partial_count, replace=False)

    if "tenure" in current_df.columns:
        current_df.loc[partial_indices, "tenure"] = (
            current_df.loc[partial_indices, "tenure"].fillna(0) * 0.55
        ).round()

    if "MonthlyCharges" in current_df.columns:
        current_df.loc[partial_indices, "MonthlyCharges"] = (
            current_df.loc[partial_indices, "MonthlyCharges"].fillna(0) * 1.3
        ).round(2)

    if {"tenure", "MonthlyCharges", "TotalCharges"}.issubset(current_df.columns):
        current_df["TotalCharges"] = (
            current_df["tenure"].fillna(0) * current_df["MonthlyCharges"].fillna(0)
        ).round(2)

    if "Contract" in current_df.columns:
        current_df.loc[majority_indices, "Contract"] = "Month-to-month"

    if "InternetService" in current_df.columns:
        current_df.loc[majority_indices, "InternetService"] = "Fiber optic"

    if "churn_probability" in current_df.columns:
        current_df["churn_probability"] = (
            current_df["churn_probability"].fillna(0).astype(float) + 0.15
        ).clip(upper=1.0)

    if "risk_label" in current_df.columns and "churn_probability" in current_df.columns:
        current_df["risk_label"] = current_df["churn_probability"].apply(
            risk_label_from_probability
        )

    return current_df


def compute_numerical_drift(
    reference_df: pd.DataFrame,
    current_df: pd.DataFrame,
    features: list[str],
    threshold: float = 0.20,
) -> dict[str, dict[str, Any]]:
    """Compute simple mean-based drift checks for numerical features."""
    results: dict[str, dict[str, Any]] = {}
    for feature in features:
        reference_mean = float(reference_df[feature].mean())
        current_mean = float(current_df[feature].mean())
        absolute_difference = current_mean - reference_mean
        if reference_mean == 0:
            percentage_difference = None
            drift_flag = absolute_difference != 0
        else:
            percentage_difference = absolute_difference / abs(reference_mean)
            drift_flag = abs(percentage_difference) >= threshold

        results[feature] = {
            "reference_mean": round(reference_mean, 4),
            "current_mean": round(current_mean, 4),
            "absolute_difference": round(float(absolute_difference), 4),
            "percentage_difference": (
                None if percentage_difference is None else round(float(percentage_difference), 4)
            ),
            "threshold": threshold,
            "drift_flag": bool(drift_flag),
        }

    return results


def _proportion_distribution(series: pd.Series) -> dict[str, float]:
    distribution = series.fillna("missing").astype(str).value_counts(normalize=True)
    return {str(key): round(float(value), 4) for key, value in sorted(distribution.items())}


def compute_categorical_drift(
    reference_df: pd.DataFrame,
    current_df: pd.DataFrame,
    features: list[str],
    threshold: float = 0.25,
) -> dict[str, dict[str, Any]]:
    """Compute distribution-shift checks for categorical features."""
    results: dict[str, dict[str, Any]] = {}
    for feature in features:
        reference_distribution = _proportion_distribution(reference_df[feature])
        current_distribution = _proportion_distribution(current_df[feature])
        categories = sorted(set(reference_distribution) | set(current_distribution))
        max_difference = max(
            abs(current_distribution.get(category, 0.0) - reference_distribution.get(category, 0.0))
            for category in categories
        )

        results[feature] = {
            "reference_distribution": reference_distribution,
            "current_distribution": current_distribution,
            "max_absolute_proportion_difference": round(float(max_difference), 4),
            "threshold": threshold,
            "drift_flag": bool(max_difference >= threshold),
        }

    return results


def build_drift_report(reference_df: pd.DataFrame, current_df: pd.DataFrame) -> dict[str, Any]:
    """Build a complete simulated drift report."""
    numerical_drift = compute_numerical_drift(
        reference_df,
        current_df,
        NUMERICAL_FEATURES,
    )
    categorical_drift = compute_categorical_drift(
        reference_df,
        current_df,
        CATEGORICAL_FEATURES,
    )
    overall_drift_detected = any(
        feature_result["drift_flag"]
        for feature_result in [*numerical_drift.values(), *categorical_drift.values()]
    )

    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "reference_record_count": int(len(reference_df)),
        "current_record_count": int(len(current_df)),
        "simulation_note": SIMULATION_NOTE,
        "numerical_drift": numerical_drift,
        "categorical_drift": categorical_drift,
        "overall_drift_detected": bool(overall_drift_detected),
    }
