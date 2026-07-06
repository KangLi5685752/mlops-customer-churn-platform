import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.monitoring.prediction_logger import MONITORING_FEATURES, log_prediction_event


def make_customer_payload() -> dict[str, str | int | float]:
    return {
        "gender": "Female",
        "SeniorCitizen": 0,
        "Partner": "Yes",
        "Dependents": "No",
        "tenure": 12,
        "PhoneService": "Yes",
        "MultipleLines": "No",
        "InternetService": "DSL",
        "OnlineSecurity": "Yes",
        "OnlineBackup": "No",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "No",
        "StreamingMovies": "No",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 59.9,
        "TotalCharges": 718.8,
    }


def test_log_prediction_event_writes_one_jsonl_line_and_creates_parent_dir(tmp_path) -> None:
    log_path = tmp_path / "logs" / "predictions.jsonl"

    record = log_prediction_event(
        churn_probability=0.75,
        churn_prediction=1,
        risk_label="high",
        customer_payload=make_customer_payload(),
        model_artifact_path="artifacts/model_pipeline.joblib",
        log_path=log_path,
    )

    assert log_path.exists()
    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    written_record = json.loads(lines[0])
    assert written_record == record
    assert "timestamp_utc" in written_record
    assert "request_id" in written_record
    assert written_record["model_artifact_path"] == "artifacts/model_pipeline.joblib"
    assert written_record["churn_probability"] == 0.75
    assert written_record["churn_prediction"] == 1
    assert written_record["risk_label"] == "high"
    assert set(written_record["monitoring_features"]) == set(MONITORING_FEATURES)
    assert written_record["monitoring_features"] == {
        "tenure": 12,
        "MonthlyCharges": 59.9,
        "TotalCharges": 718.8,
        "Contract": "Month-to-month",
        "InternetService": "DSL",
        "PaymentMethod": "Electronic check",
    }
