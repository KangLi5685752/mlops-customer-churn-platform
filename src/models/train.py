"""Train baseline Telco churn models from the command line."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from src.data.load_data import clean_telco_data, load_raw_data, split_features_target
from src.features.preprocessing import (
    build_dummy_pipeline,
    build_logistic_regression_pipeline,
)
from src.utils.paths import MODEL_ARTIFACT_PATH, PROJECT_ROOT, RAW_DATA_PATH, REPORTS_DIR

RANDOM_STATE = 42
TEST_SIZE = 0.2
TRAINING_METRICS_PATH = REPORTS_DIR / "training_metrics.json"
REPORT_DATASET_PATH = RAW_DATA_PATH.relative_to(PROJECT_ROOT).as_posix()
REPORT_MODEL_ARTIFACT_PATH = MODEL_ARTIFACT_PATH.relative_to(PROJECT_ROOT).as_posix()


def evaluate_classifier(model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict[str, Any]:
    """Evaluate a fitted classifier on the held-out churn test set."""
    y_pred = model.predict(X_test)

    roc_auc = None
    if hasattr(model, "predict_proba"):
        y_proba = model.predict_proba(X_test)[:, 1]
        roc_auc = roc_auc_score(y_test, y_proba)

    return {
        "roc_auc": None if roc_auc is None else round(float(roc_auc), 4),
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred, labels=[0, 1]).tolist(),
    }


def format_metrics_line(model_name: str, metrics: dict[str, Any]) -> str:
    """Format a compact one-line metrics summary for console output."""
    return (
        f"{model_name}: "
        f"roc_auc={metrics['roc_auc']}, "
        f"accuracy={metrics['accuracy']}, "
        f"precision={metrics['precision']}, "
        f"recall={metrics['recall']}, "
        f"f1={metrics['f1']}"
    )


def build_training_payload(
    raw_df: pd.DataFrame,
    X: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    metrics: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Build the serialisable training metrics payload."""
    target_distribution = {
        str(label): int(count)
        for label, count in raw_df["Churn"].value_counts().sort_index().items()
    }

    return {
        "dataset_path": REPORT_DATASET_PATH,
        "n_rows": int(raw_df.shape[0]),
        "n_columns": int(raw_df.shape[1]),
        "n_features": int(X.shape[1]),
        "target_distribution": target_distribution,
        "train_size": int(len(y_train)),
        "test_size": int(len(y_test)),
        "model_artifact_path": REPORT_MODEL_ARTIFACT_PATH,
        "models": list(metrics.keys()),
        "metrics": metrics,
        "run_date": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    """Train baseline models and save the LogisticRegression pipeline artifact."""
    raw_df = load_raw_data()
    cleaned_df = clean_telco_data(raw_df)
    X, y = split_features_target(cleaned_df)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    dummy_pipeline = build_dummy_pipeline(X_train)
    logistic_pipeline = build_logistic_regression_pipeline(X_train)

    dummy_pipeline.fit(X_train, y_train)
    logistic_pipeline.fit(X_train, y_train)

    metrics = {
        "DummyClassifier": evaluate_classifier(dummy_pipeline, X_test, y_test),
        "LogisticRegression": evaluate_classifier(logistic_pipeline, X_test, y_test),
    }

    MODEL_ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(logistic_pipeline, MODEL_ARTIFACT_PATH)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_training_payload(raw_df, X, y_train, y_test, metrics)
    TRAINING_METRICS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("Training completed")
    print(f"Dataset: {RAW_DATA_PATH}")
    print(f"Rows: {raw_df.shape[0]}, columns: {raw_df.shape[1]}, features: {X.shape[1]}")
    print(f"Train size: {len(y_train)}, test size: {len(y_test)}")
    for model_name, model_metrics in metrics.items():
        print(format_metrics_line(model_name, model_metrics))
    print(f"Saved model pipeline artifact to {MODEL_ARTIFACT_PATH}")
    print(f"Saved training metrics to {TRAINING_METRICS_PATH}")


if __name__ == "__main__":
    main()
