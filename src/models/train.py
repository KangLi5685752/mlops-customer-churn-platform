"""Train baseline Telco churn models from the command line."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import mlflow
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
MLFLOW_RUN_SUMMARY_PATH = REPORTS_DIR / "mlflow_run_summary.md"
MLFLOW_EXPERIMENT_NAME = "telco-churn-baseline"
MLFLOW_TRACKING_URI = (PROJECT_ROOT / "mlruns").as_uri()
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


def log_mlflow_metrics(metrics: dict[str, dict[str, Any]]) -> None:
    """Log scalar model metrics to the active MLflow run."""
    for metric_name, metric_value in metrics["LogisticRegression"].items():
        if metric_name != "confusion_matrix" and metric_value is not None:
            mlflow.log_metric(metric_name, float(metric_value))

    for metric_name, metric_value in metrics["DummyClassifier"].items():
        if metric_name != "confusion_matrix" and metric_value is not None:
            mlflow.log_metric(f"dummy_{metric_name}", float(metric_value))


def build_mlflow_run_summary(run_id: str, metrics: dict[str, dict[str, Any]]) -> str:
    """Build a concise local MLflow run summary for the reports directory."""
    logistic_metrics = metrics["LogisticRegression"]
    dummy_metrics = metrics["DummyClassifier"]

    return "\n".join(
        [
            "# MLflow Run Summary",
            "",
            f"- Experiment name: `{MLFLOW_EXPERIMENT_NAME}`",
            f"- Run ID: `{run_id}`",
            "- Logged model type: `LogisticRegression`",
            "- Baseline model: `DummyClassifier`",
            f"- Model artifact path: `{REPORT_MODEL_ARTIFACT_PATH}`",
            f"- Training metrics report: `{TRAINING_METRICS_PATH.relative_to(PROJECT_ROOT).as_posix()}`",
            "",
            "## LogisticRegression Metrics",
            "",
            f"- ROC-AUC: {logistic_metrics['roc_auc']}",
            f"- Accuracy: {logistic_metrics['accuracy']}",
            f"- Precision: {logistic_metrics['precision']}",
            f"- Recall: {logistic_metrics['recall']}",
            f"- F1: {logistic_metrics['f1']}",
            "",
            "## DummyClassifier Metrics",
            "",
            f"- ROC-AUC: {dummy_metrics['roc_auc']}",
            f"- Accuracy: {dummy_metrics['accuracy']}",
            f"- Precision: {dummy_metrics['precision']}",
            f"- Recall: {dummy_metrics['recall']}",
            f"- F1: {dummy_metrics['f1']}",
            "",
            "## Local MLflow UI",
            "",
            "Start the local UI from the project root:",
            "",
            "```bash",
            "mlflow ui",
            "```",
            "",
            "Open:",
            "",
            "```text",
            "http://127.0.0.1:5000",
            "```",
            "",
        ]
    )


def write_mlflow_run_summary(run_id: str, metrics: dict[str, dict[str, Any]]) -> bool:
    """Write the local MLflow run summary without masking training success."""
    try:
        MLFLOW_RUN_SUMMARY_PATH.write_text(
            build_mlflow_run_summary(run_id, metrics),
            encoding="utf-8",
        )
    except OSError as exc:
        print(f"Warning: could not write MLflow run summary: {exc}")
        return False
    return True


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

    os.environ.setdefault("MLFLOW_ALLOW_FILE_STORE", "true")
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

    with mlflow.start_run() as run:
        mlflow.log_params(
            {
                "model_type": "LogisticRegression",
                "baseline_model": "DummyClassifier",
                "test_size": TEST_SIZE,
                "random_state": RANDOM_STATE,
                "target": "Churn",
                "artifact_path": REPORT_MODEL_ARTIFACT_PATH,
            }
        )

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

        log_mlflow_metrics(metrics)
        mlflow.log_artifact(str(TRAINING_METRICS_PATH), artifact_path="reports")
        mlflow.log_artifact(str(MODEL_ARTIFACT_PATH), artifact_path="artifacts")

        run_id = run.info.run_id
        summary_written = write_mlflow_run_summary(run_id, metrics)
        if summary_written:
            mlflow.log_artifact(str(MLFLOW_RUN_SUMMARY_PATH), artifact_path="reports")

    print("Training completed")
    print(f"Dataset: {RAW_DATA_PATH}")
    print(f"Rows: {raw_df.shape[0]}, columns: {raw_df.shape[1]}, features: {X.shape[1]}")
    print(f"Train size: {len(y_train)}, test size: {len(y_test)}")
    for model_name, model_metrics in metrics.items():
        print(format_metrics_line(model_name, model_metrics))
    print(f"Saved model pipeline artifact to {MODEL_ARTIFACT_PATH}")
    print(f"Saved training metrics to {TRAINING_METRICS_PATH}")
    if summary_written:
        print(f"Saved MLflow run summary to {MLFLOW_RUN_SUMMARY_PATH}")
    print(f"MLflow experiment: {MLFLOW_EXPERIMENT_NAME}")
    print(f"MLflow run ID: {run_id}")
    print(f"MLflow tracking URI: {MLFLOW_TRACKING_URI}")


if __name__ == "__main__":
    main()
