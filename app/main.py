"""FastAPI app for serving the saved Telco churn model pipeline."""

from functools import lru_cache
from typing import Any

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from sklearn.pipeline import Pipeline

from app.schemas import FEATURE_COLUMNS, PredictionResponse, TelcoCustomerRequest
from src.utils.paths import MODEL_ARTIFACT_PATH, PROJECT_ROOT

MODEL_ARTIFACT_RELATIVE_PATH = MODEL_ARTIFACT_PATH.relative_to(PROJECT_ROOT).as_posix()
MISSING_MODEL_MESSAGE = (
    f"Model artifact not found at {MODEL_ARTIFACT_RELATIVE_PATH}. "
    "Run `python -m src.models.train` first."
)

app = FastAPI(
    title="Telco Customer Churn Prediction API",
    version="0.1.0",
    description="Local FastAPI app for serving the saved Telco churn model pipeline.",
)


@lru_cache(maxsize=1)
def load_model_pipeline() -> Pipeline:
    """Load the saved preprocessing and LogisticRegression pipeline artifact."""
    if not MODEL_ARTIFACT_PATH.exists():
        raise FileNotFoundError(MISSING_MODEL_MESSAGE)

    return joblib.load(MODEL_ARTIFACT_PATH)


def customer_to_dataframe(customer: TelcoCustomerRequest) -> pd.DataFrame:
    """Convert a request payload into a one-row DataFrame with training columns."""
    if hasattr(customer, "model_dump"):
        payload: dict[str, Any] = customer.model_dump()
    else:
        payload = customer.dict()

    return pd.DataFrame([{column: payload[column] for column in FEATURE_COLUMNS}])


def risk_label_from_probability(churn_probability: float) -> str:
    """Map churn probability to a simple prototype risk label."""
    if churn_probability >= 0.65:
        return "high"
    if churn_probability >= 0.35:
        return "medium"
    return "low"


@app.get("/health")
def health() -> dict[str, str | bool]:
    """Return basic API and model-artifact health information."""
    return {
        "status": "ok",
        "model_artifact_path": MODEL_ARTIFACT_RELATIVE_PATH,
        "model_artifact_exists": MODEL_ARTIFACT_PATH.exists(),
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(customer: TelcoCustomerRequest) -> PredictionResponse:
    """Predict churn probability and risk label for one Telco customer."""
    try:
        model_pipeline = load_model_pipeline()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    input_df = customer_to_dataframe(customer)
    churn_probability = float(model_pipeline.predict_proba(input_df)[0, 1])
    churn_prediction = int(model_pipeline.predict(input_df)[0])

    return PredictionResponse(
        churn_probability=churn_probability,
        churn_prediction=churn_prediction,
        risk_label=risk_label_from_probability(churn_probability),
    )
