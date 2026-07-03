import sys
from pathlib import Path

import pandas as pd
from sklearn.pipeline import Pipeline

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.features.preprocessing import build_dummy_pipeline, build_logistic_regression_pipeline


def make_synthetic_features() -> tuple[pd.DataFrame, pd.Series]:
    X = pd.DataFrame(
        {
            "gender": ["Female", "Male", "Female", "Male", "Female", "Male"],
            "SeniorCitizen": [0, 1, 0, 1, 0, 1],
            "Partner": ["Yes", "No", "Yes", "No", "No", "Yes"],
            "tenure": [1, 2, 12, 24, 36, 48],
            "Contract": [
                "Month-to-month",
                "Month-to-month",
                "One year",
                "Two year",
                "One year",
                "Two year",
            ],
            "MonthlyCharges": [29.85, 70.70, 45.30, 20.00, 65.20, 89.10],
            "TotalCharges": [29.85, None, 543.60, 480.00, 2347.20, 4276.80],
            "PaymentMethod": [
                "Electronic check",
                "Electronic check",
                "Mailed check",
                "Bank transfer (automatic)",
                "Credit card (automatic)",
                "Mailed check",
            ],
        }
    )
    y = pd.Series([0, 1, 0, 0, 1, 1], name="Churn")
    return X, y


def test_logistic_regression_pipeline_can_fit_predict_and_predict_proba() -> None:
    X, y = make_synthetic_features()

    pipeline = build_logistic_regression_pipeline(X)
    pipeline.fit(X, y)

    predictions = pipeline.predict(X)
    probabilities = pipeline.predict_proba(X)

    assert isinstance(pipeline, Pipeline)
    assert len(predictions) == len(X)
    assert probabilities.shape == (len(X), 2)


def test_dummy_pipeline_can_fit_and_predict() -> None:
    X, y = make_synthetic_features()

    pipeline = build_dummy_pipeline(X)
    pipeline.fit(X, y)
    predictions = pipeline.predict(X)

    assert isinstance(pipeline, Pipeline)
    assert len(predictions) == len(X)
