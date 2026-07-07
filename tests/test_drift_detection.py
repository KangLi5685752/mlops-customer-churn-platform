import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.monitoring.drift_detection import (
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
    build_drift_report,
    compute_categorical_drift,
    compute_numerical_drift,
    prediction_events_to_dataframe,
    simulate_current_batch,
)


def sample_prediction_events() -> list[dict]:
    return [
        {
            "churn_probability": 0.2,
            "risk_label": "low",
            "monitoring_features": {
                "tenure": 12,
                "MonthlyCharges": 59.9,
                "TotalCharges": 718.8,
                "Contract": "Month-to-month",
                "InternetService": "DSL",
                "PaymentMethod": "Electronic check",
            },
        },
        {
            "churn_probability": 0.72,
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
            "churn_probability": 0.33,
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


def test_prediction_events_to_dataframe_extracts_monitoring_columns() -> None:
    df = prediction_events_to_dataframe(sample_prediction_events())

    expected_columns = set(NUMERICAL_FEATURES + CATEGORICAL_FEATURES)
    assert expected_columns.issubset(df.columns)
    assert len(df) == 3
    assert df.loc[0, "tenure"] == 12
    assert df.loc[1, "risk_label"] == "high"


def test_simulate_current_batch_preserves_row_count_and_required_columns() -> None:
    reference_df = prediction_events_to_dataframe(sample_prediction_events())

    current_df = simulate_current_batch(reference_df, random_seed=7)

    assert len(current_df) == len(reference_df)
    for feature in NUMERICAL_FEATURES + CATEGORICAL_FEATURES:
        assert feature in current_df.columns


def test_compute_numerical_drift_flags_clear_mean_shift() -> None:
    reference_df = pd.DataFrame({"tenure": [10, 10, 10]})
    current_df = pd.DataFrame({"tenure": [20, 20, 20]})

    result = compute_numerical_drift(
        reference_df,
        current_df,
        ["tenure"],
        threshold=0.2,
    )

    assert result["tenure"]["reference_mean"] == 10.0
    assert result["tenure"]["current_mean"] == 20.0
    assert result["tenure"]["drift_flag"] is True


def test_compute_categorical_drift_flags_clear_distribution_shift() -> None:
    reference_df = pd.DataFrame({"Contract": ["Month-to-month", "Two year", "Two year"]})
    current_df = pd.DataFrame({"Contract": ["Month-to-month", "Month-to-month", "Month-to-month"]})

    result = compute_categorical_drift(
        reference_df,
        current_df,
        ["Contract"],
        threshold=0.25,
    )

    assert result["Contract"]["max_absolute_proportion_difference"] >= 0.5
    assert result["Contract"]["drift_flag"] is True


def test_build_drift_report_returns_expected_top_level_keys() -> None:
    reference_df = prediction_events_to_dataframe(sample_prediction_events())
    current_df = simulate_current_batch(reference_df, random_seed=42)

    report = build_drift_report(reference_df, current_df)

    assert {
        "timestamp_utc",
        "reference_record_count",
        "current_record_count",
        "simulation_note",
        "numerical_drift",
        "categorical_drift",
        "overall_drift_detected",
    }.issubset(report)
