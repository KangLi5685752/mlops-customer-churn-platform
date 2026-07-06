import json
import sys
from pathlib import Path

import numpy as np
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app.main as app_main


def valid_customer_payload() -> dict[str, str | int | float]:
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


def test_health_endpoint_returns_api_and_model_artifact_status() -> None:
    client = TestClient(app_main.app)

    response = client.get("/health")

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["status"] == "ok"
    assert "model_artifact_path" in response_json
    assert "model_artifact_exists" in response_json


def test_predict_endpoint_returns_prediction_with_mocked_pipeline(monkeypatch, tmp_path) -> None:
    class FakeModelPipeline:
        def predict_proba(self, X):
            return np.array([[0.25, 0.75]])

        def predict(self, X):
            return np.array([1])

    def fake_load_model_pipeline():
        return FakeModelPipeline()

    monkeypatch.setattr(app_main, "load_model_pipeline", fake_load_model_pipeline)
    log_path = tmp_path / "logs" / "predictions.jsonl"
    monkeypatch.setattr(app_main, "PREDICTION_LOG_PATH", log_path)
    client = TestClient(app_main.app)

    response = client.post("/predict", json=valid_customer_payload())

    assert response.status_code == 200
    response_json = response.json()
    assert "churn_probability" in response_json
    assert "churn_prediction" in response_json
    assert "risk_label" in response_json
    assert response_json["churn_probability"] == 0.75
    assert response_json["churn_prediction"] == 1
    assert response_json["risk_label"] == "high"


def test_predict_endpoint_writes_prediction_log_with_mocked_pipeline(monkeypatch, tmp_path) -> None:
    class FakeModelPipeline:
        def predict_proba(self, X):
            return np.array([[0.72, 0.28]])

        def predict(self, X):
            return np.array([0])

    def fake_load_model_pipeline():
        return FakeModelPipeline()

    log_path = tmp_path / "logs" / "predictions.jsonl"
    monkeypatch.setattr(app_main, "load_model_pipeline", fake_load_model_pipeline)
    monkeypatch.setattr(app_main, "PREDICTION_LOG_PATH", log_path)
    client = TestClient(app_main.app)

    response = client.post("/predict", json=valid_customer_payload())

    assert response.status_code == 200
    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    log_record = json.loads(lines[0])
    assert log_record["churn_probability"] == 0.28
    assert log_record["churn_prediction"] == 0
    assert log_record["risk_label"] == "low"
    assert log_record["monitoring_features"] == {
        "tenure": 12,
        "MonthlyCharges": 59.9,
        "TotalCharges": 718.8,
        "Contract": "Month-to-month",
        "InternetService": "DSL",
        "PaymentMethod": "Electronic check",
    }


def test_predict_endpoint_returns_503_when_model_artifact_is_missing(monkeypatch) -> None:
    def fake_load_model_pipeline():
        raise FileNotFoundError(
            "Model artifact not found. Run `python -m src.models.train` first."
        )

    monkeypatch.setattr(app_main, "load_model_pipeline", fake_load_model_pipeline)
    client = TestClient(app_main.app)

    response = client.post("/predict", json=valid_customer_payload())

    assert response.status_code == 503
    assert "model artifact" in response.json()["detail"].lower()
    assert "python -m src.models.train" in response.json()["detail"]


def test_predict_endpoint_returns_422_for_invalid_payload() -> None:
    client = TestClient(app_main.app)
    payload = valid_customer_payload()
    payload.pop("gender")

    response = client.post("/predict", json=payload)

    assert response.status_code == 422
