import sys
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.load_data import clean_telco_data, split_features_target
from src.features.preprocessing import build_preprocessor, get_feature_types


def make_cleaned_features() -> pd.DataFrame:
    raw_df = pd.DataFrame(
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
            "TotalCharges": ["29.85", "", "500.50"],
            "Churn": ["No", "Yes", "No"],
        }
    )
    cleaned_df = clean_telco_data(raw_df)
    X, _ = split_features_target(cleaned_df)
    return X


def test_get_feature_types_identifies_expected_telco_features() -> None:
    X = make_cleaned_features()

    numerical_features, categorical_features = get_feature_types(X)

    assert numerical_features == [
        "SeniorCitizen",
        "tenure",
        "MonthlyCharges",
        "TotalCharges",
    ]
    assert "gender" in categorical_features
    assert "Contract" in categorical_features
    assert "PaymentMethod" in categorical_features


def test_build_preprocessor_can_fit_transform_cleaned_features() -> None:
    X = make_cleaned_features()
    numerical_features, categorical_features = get_feature_types(X)

    preprocessor = build_preprocessor(numerical_features, categorical_features)
    transformed = preprocessor.fit_transform(X)

    assert isinstance(preprocessor, ColumnTransformer)
    assert transformed.shape[0] == len(X)
