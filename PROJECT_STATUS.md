# Project Status

## Current Phase

Stage 2 baseline notebook and initial evaluation completed locally.

## Completed in This Step

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

Refactor baseline logic into reusable training and evaluation scripts under `src`.

## Known Risks

- The public dataset is small and may not represent real customer populations.
- Future simulated production traffic may not reflect real production data.
- Churn probability can be misused if treated as an automatic customer treatment decision.
- Drift monitoring in this portfolio project will be simulated rather than based on live production data.
- Scope could expand too quickly if cloud deployment, Kubernetes or streaming systems are added too early.
- Baseline metrics may change if the dataset version or preprocessing assumptions change.

## Current Status Summary

The project now has an experimentation-stage Telco churn baseline. The notebook establishes a credible local workflow using pandas and scikit-learn, compares a dummy sanity-check model with logistic regression and saves real baseline metrics from the local dataset. No model artifact, API, Docker, CI, MLflow tracking, dashboard implementation or drift detection code has been added yet.

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
