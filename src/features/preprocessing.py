"""Reusable preprocessing and baseline pipeline builders."""

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERICAL_FEATURE_CANDIDATES = [
    "SeniorCitizen",
    "tenure",
    "MonthlyCharges",
    "TotalCharges",
]
RANDOM_STATE = 42


def get_feature_types(X: pd.DataFrame) -> tuple[list[str], list[str]]:
    """Return numerical and categorical feature names for the Telco churn data."""
    numerical_features = [
        feature for feature in NUMERICAL_FEATURE_CANDIDATES if feature in X.columns
    ]
    categorical_features = [
        feature for feature in X.columns if feature not in numerical_features
    ]
    return numerical_features, categorical_features


def build_preprocessor(
    numerical_features: list[str], categorical_features: list[str]
) -> ColumnTransformer:
    """Build the scikit-learn preprocessing transformer used by baseline models."""
    numerical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numerical_pipeline, numerical_features),
            ("cat", categorical_pipeline, categorical_features),
        ]
    )


def build_logistic_regression_pipeline(X: pd.DataFrame) -> Pipeline:
    """Build the first reasonable LogisticRegression baseline pipeline."""
    numerical_features, categorical_features = get_feature_types(X)
    preprocessor = build_preprocessor(numerical_features, categorical_features)

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)),
        ]
    )


def build_dummy_pipeline(X: pd.DataFrame) -> Pipeline:
    """Build a DummyClassifier sanity-check baseline pipeline."""
    numerical_features, categorical_features = get_feature_types(X)
    preprocessor = build_preprocessor(numerical_features, categorical_features)

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", DummyClassifier(strategy="prior", random_state=RANDOM_STATE)),
        ]
    )
