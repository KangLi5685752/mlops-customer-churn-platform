import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.load_data import clean_telco_data, split_features_target


def make_telco_like_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customerID": ["0001-A", "0002-B", "0003-C"],
            "gender": ["Female", "Male", "Female"],
            "SeniorCitizen": [0, 1, 0],
            "Partner": ["Yes", "No", "No"],
            "Dependents": ["No", "No", "Yes"],
            "tenure": [1, 12, 24],
            "PhoneService": ["No", "Yes", "Yes"],
            "MultipleLines": ["No phone service", "No", "Yes"],
            "InternetService": ["DSL", "Fiber optic", "No"],
            "OnlineSecurity": ["No", "Yes", "No internet service"],
            "OnlineBackup": ["Yes", "No", "No internet service"],
            "DeviceProtection": ["No", "Yes", "No internet service"],
            "TechSupport": ["No", "No", "No internet service"],
            "StreamingTV": ["No", "Yes", "No internet service"],
            "StreamingMovies": ["No", "No", "No internet service"],
            "Contract": ["Month-to-month", "One year", "Two year"],
            "PaperlessBilling": ["Yes", "No", "No"],
            "PaymentMethod": [
                "Electronic check",
                "Mailed check",
                "Bank transfer (automatic)",
            ],
            "MonthlyCharges": [29.85, 56.95, 20.0],
            "TotalCharges": ["29.85", "not-a-number", ""],
            "Churn": ["No", "Yes", "No"],
        }
    )


def test_clean_telco_data_drops_id_converts_total_charges_and_maps_target() -> None:
    cleaned_df = clean_telco_data(make_telco_like_dataframe())

    assert "customerID" not in cleaned_df.columns
    assert pd.api.types.is_numeric_dtype(cleaned_df["TotalCharges"])
    assert cleaned_df["TotalCharges"].isna().sum() == 2
    assert cleaned_df["Churn"].tolist() == [0, 1, 0]


def test_split_features_target_returns_features_without_target_and_binary_y() -> None:
    cleaned_df = clean_telco_data(make_telco_like_dataframe())

    X, y = split_features_target(cleaned_df)

    assert "Churn" not in X.columns
    assert set(y.unique()) == {0, 1}
    assert len(X) == len(y)


def test_clean_telco_data_raises_clear_error_when_churn_missing() -> None:
    raw_df = make_telco_like_dataframe().drop(columns=["Churn"])

    with pytest.raises(ValueError, match="Expected target column 'Churn'"):
        clean_telco_data(raw_df)
