# Project Status

## Current Phase

Stage 3A reusable data and preprocessing modules completed locally.

## Completed in This Step

- Added reusable path helpers in `src/utils/paths.py`.
- Added reusable Telco churn data loading, cleaning and feature/target split helpers in `src/data/load_data.py`.
- Added reusable preprocessing, dummy baseline pipeline and logistic regression pipeline builders in `src/features/preprocessing.py`.
- Added package `__init__.py` files under `src`, `src/utils`, `src/data` and `src/features`.
- Preserved Stage 2 notebook and metric reports without adding new training scripts or model artifacts.

## Previous Stage 2 Completion

- Created `notebooks/01_baseline_experiment.ipynb` for the Telco churn baseline experiment.
- Loaded the dataset from `data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv` using repository-relative paths.
- Added basic EDA for shape, first rows, column types, target distribution, missing values, `TotalCharges` blanks and numeric summaries.
- Dropped `customerID` as an identifier before modelling.
- Converted `TotalCharges` to numeric and handled missing values through median imputation in the preprocessing pipeline.
- Encoded `Churn` as the positive class where `Yes = 1` and `No = 0`.
- Trained and evaluated `DummyClassifier` as a sanity-check baseline.
- Trained and evaluated `LogisticRegression` as the first reasonable baseline model.
- Generated `reports/baseline_metrics.json` and `reports/baseline_summary.md` from the real local dataset run.
- Updated README data setup and baseline experiment notes.
- Updated the decision log with baseline-stage modelling and data-cleaning decisions.

## Next Planned Task

Create command-line training and evaluation scripts under `src/models` using the reusable Stage 3A modules.

## Known Risks

- The public dataset is small and may not represent real customer populations.
- Future simulated production traffic may not reflect real production data.
- Churn probability can be misused if treated as an automatic customer treatment decision.
- Drift monitoring in this portfolio project will be simulated rather than based on live production data.
- Scope could expand too quickly if cloud deployment, Kubernetes or streaming systems are added too early.
- Baseline metrics may change if the dataset version or preprocessing assumptions change.

## Current Status Summary

The project now has reusable Stage 3A modules for repository-relative paths, raw data loading, Telco-specific cleaning, feature/target splitting and baseline preprocessing pipeline construction. The Stage 2 notebook and reports remain in place. No training script, model artifact, API, Docker, CI, MLflow tracking, dashboard implementation or drift detection code has been added yet.

## Project Evidence and Validation Artifacts to Collect

- Held-out model evaluation metrics from `reports/baseline_metrics.json`.
- Baseline interpretation from `reports/baseline_summary.md`.
- Before/after comparison between baseline notebook workflow and refactored MLOps workflow.
- API request and response examples.
- API average and p95 latency from local benchmarking.
- pytest test count and passing test output.
- GitHub Actions CI pass/fail evidence.
- MLflow experiment run screenshots or summaries.
- Prediction log examples.
- Simulated drift detection output.
- Streamlit monitoring dashboard screenshot.
- Final model card and risk register content.

## Milestone Log

- 2026-06-26: Initialized repository structure, documentation templates and MVP scope for the Telco churn MLOps project.
- 2026-06-27: Added and executed the baseline Telco churn notebook, generating local baseline metrics and summary reports.
- 2026-06-29: Added reusable path, data loading, cleaning and preprocessing modules for Stage 3A.
