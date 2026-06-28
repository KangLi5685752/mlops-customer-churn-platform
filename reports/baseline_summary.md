# Baseline Experiment Summary

## Baseline Purpose

This baseline establishes a reasonable experimentation-stage churn prediction workflow before adding production-style MLOps components.

## Dataset Summary

- Dataset path: `D:\Warwick\Portfolio Plan\portfolio-projects\mlops-customer-churn-platform\data\raw\WA_Fn-UseC_-Telco-Customer-Churn.csv`
- Rows: 7043
- Columns: 21
- Features after dropping `customerID` and `Churn`: 19

## Target Distribution

- No: 5174
- Yes: 1869

## TotalCharges Cleaning Note

`TotalCharges` was converted to numeric with `pandas.to_numeric(..., errors="coerce")`. Missing values after conversion: 11. These missing values are handled with median imputation inside the preprocessing pipeline.

## Metrics Table

| model | roc_auc | accuracy | precision | recall | f1 |
|---|---|---|---|---|---|
| DummyClassifier | 0.5 | 0.7346 | 0.0 | 0.0 | 0.0 |
| LogisticRegression | 0.8419 | 0.8055 | 0.6572 | 0.5588 | 0.604 |

## Confusion Matrices

- DummyClassifier: [[1035, 0], [374, 0]]
- LogisticRegression: [[926, 109], [165, 209]]

## Short Interpretation

`DummyClassifier` is a sanity-check baseline, not a meaningful churn model. `LogisticRegression` is the first reasonable baseline because it combines standard tabular preprocessing with a simple classifier that is easy to inspect and later refactor.

## Baseline Limitations

This stage does not include API serving, Docker, automated tests, MLflow tracking, prediction logging or drift monitoring. The dataset is public and limited, and results should not be treated as evidence of real production performance or real business impact.

## Next Step

Refactor the baseline logic into reusable training and evaluation scripts under `src`.
