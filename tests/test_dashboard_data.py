import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.monitoring.dashboard_data import (
    load_drift_results,
    load_prediction_logs,
    prepare_risk_label_counts,
    summarise_prediction_logs,
)


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(record) for record in records) + "\n",
        encoding="utf-8",
    )


def sample_prediction_records() -> list[dict]:
    return [
        {
            "timestamp_utc": "2026-07-07T10:00:00+00:00",
            "request_id": "request-1",
            "model_artifact_path": "artifacts/model_pipeline.joblib",
            "churn_probability": 0.72,
            "churn_prediction": 1,
            "risk_label": "high",
            "monitoring_features": {
                "tenure": 3,
                "MonthlyCharges": 95.4,
                "TotalCharges": 286.2,
                "Contract": "Month-to-month",
                "InternetService": "Fiber optic",
                "PaymentMethod": "Electronic check",
            },
        },
        {
            "timestamp_utc": "2026-07-07T10:05:00+00:00",
            "request_id": "request-2",
            "model_artifact_path": "artifacts/model_pipeline.joblib",
            "churn_probability": 0.25,
            "churn_prediction": 0,
            "risk_label": "low",
            "monitoring_features": {
                "tenure": 48,
                "MonthlyCharges": 64.2,
                "TotalCharges": 3081.6,
                "Contract": "Two year",
                "InternetService": "DSL",
                "PaymentMethod": "Credit card (automatic)",
            },
        },
    ]


def test_load_prediction_logs_flattens_monitoring_features(tmp_path) -> None:
    log_path = tmp_path / "predictions.jsonl"
    write_jsonl(log_path, sample_prediction_records())

    df = load_prediction_logs(log_path)

    assert len(df) == 2
    assert "monitoring_features" not in df.columns
    assert df.loc[0, "tenure"] == 3
    assert df.loc[0, "InternetService"] == "Fiber optic"
    assert df.loc[1, "PaymentMethod"] == "Credit card (automatic)"


def test_summarise_prediction_logs_computes_overview_metrics(tmp_path) -> None:
    log_path = tmp_path / "predictions.jsonl"
    write_jsonl(log_path, sample_prediction_records())
    df = load_prediction_logs(log_path)

    summary = summarise_prediction_logs(df)

    assert summary["total_prediction_events"] == 2
    assert summary["latest_prediction_timestamp"] == "2026-07-07T10:05:00+00:00"
    assert summary["average_churn_probability"] == 0.485
    assert summary["high_risk_percentage"] == 50.0
    assert summary["risk_label_counts"] == {"low": 1, "medium": 0, "high": 1}


def test_prepare_risk_label_counts_uses_stable_order(tmp_path) -> None:
    log_path = tmp_path / "predictions.jsonl"
    write_jsonl(log_path, sample_prediction_records())
    df = load_prediction_logs(log_path)

    counts = prepare_risk_label_counts(df)

    assert counts["risk_label"].tolist() == ["low", "medium", "high"]
    assert counts["count"].tolist() == [1, 0, 1]


def test_missing_prediction_log_returns_empty_dataframe(tmp_path) -> None:
    df = load_prediction_logs(tmp_path / "missing.jsonl")

    assert df.empty
    assert "churn_probability" in df.columns
    assert "Contract" in df.columns


def test_load_drift_results_returns_dict_and_handles_missing_file(tmp_path) -> None:
    drift_path = tmp_path / "drift.json"
    drift_path.write_text(
        json.dumps({"overall_drift_detected": True, "reference_record_count": 2}),
        encoding="utf-8",
    )

    assert load_drift_results(drift_path)["overall_drift_detected"] is True
    assert load_drift_results(tmp_path / "missing.json") == {}
