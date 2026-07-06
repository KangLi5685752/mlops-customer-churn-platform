"""Local JSONL prediction logging for the FastAPI inference workflow."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.utils.paths import PREDICTION_LOG_PATH

MONITORING_FEATURES = [
    "tenure",
    "MonthlyCharges",
    "TotalCharges",
    "Contract",
    "InternetService",
    "PaymentMethod",
]


def select_monitoring_features(customer_payload: dict[str, Any]) -> dict[str, Any]:
    """Select the small feature subset used for later local monitoring."""
    return {feature: customer_payload.get(feature) for feature in MONITORING_FEATURES}


def log_prediction_event(
    *,
    churn_probability: float,
    churn_prediction: int,
    risk_label: str,
    customer_payload: dict[str, Any],
    model_artifact_path: str,
    log_path: Path = PREDICTION_LOG_PATH,
) -> dict[str, Any]:
    """Append one successful prediction event to the local JSONL log."""
    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "request_id": str(uuid4()),
        "model_artifact_path": model_artifact_path,
        "churn_probability": churn_probability,
        "churn_prediction": churn_prediction,
        "risk_label": risk_label,
        "monitoring_features": select_monitoring_features(customer_payload),
    }

    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(record, sort_keys=True) + "\n")

    return record
