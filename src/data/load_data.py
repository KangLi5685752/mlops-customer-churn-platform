"""Data loading and cleaning helpers for the Telco churn dataset."""

from pathlib import Path

import pandas as pd

from src.utils.paths import RAW_DATA_PATH

TARGET_COLUMN = "Churn"
ID_COLUMN = "customerID"
TOTAL_CHARGES_COLUMN = "TotalCharges"
TARGET_MAPPING = {"No": 0, "Yes": 1}


def load_raw_data(dataset_path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Load the raw Telco churn CSV from the expected repository path."""
    dataset_path = Path(dataset_path)

    if not dataset_path.exists():
        raise FileNotFoundError(
            "Download the Telco Customer Churn CSV file named "
            "WA_Fn-UseC_-Telco-Customer-Churn.csv and place it at "
            "data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv"
        )

    return pd.read_csv(dataset_path)


def clean_telco_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the Telco churn data while preserving values for pipeline imputation."""
    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Expected target column '{TARGET_COLUMN}' in input data.")

    if TOTAL_CHARGES_COLUMN not in df.columns:
        raise ValueError(f"Expected column '{TOTAL_CHARGES_COLUMN}' in input data.")

    cleaned_df = df.copy()

    if ID_COLUMN in cleaned_df.columns:
        cleaned_df = cleaned_df.drop(columns=[ID_COLUMN])

    cleaned_df[TOTAL_CHARGES_COLUMN] = pd.to_numeric(
        cleaned_df[TOTAL_CHARGES_COLUMN], errors="coerce"
    )

    original_target = cleaned_df[TARGET_COLUMN].copy()
    cleaned_df[TARGET_COLUMN] = cleaned_df[TARGET_COLUMN].map(TARGET_MAPPING)

    unmapped_values = original_target[cleaned_df[TARGET_COLUMN].isna()].dropna().unique()
    if len(unmapped_values) > 0:
        raise ValueError(
            f"Unexpected values in '{TARGET_COLUMN}' column: {sorted(unmapped_values)}"
        )

    return cleaned_df


def split_features_target(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Split a cleaned dataframe into features and binary churn target."""
    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Expected target column '{TARGET_COLUMN}' in input data.")

    X = df.drop(columns=[TARGET_COLUMN])
    y = df[TARGET_COLUMN].astype(int)
    return X, y
