# Project Status

## Current Phase

Stage 9B final README and portfolio evidence polish.

## Completed in This Step

- README workflow clarified.
- Project evidence summary added.
- Reproducibility workflow documented.
- Limitations and safe claims clarified.

## Previous Stage 9A Completion

- Added local Streamlit dashboard for prediction logs and simulated drift reports.
- Displayed prediction event count, risk label distribution and churn probability summaries.
- Displayed monitoring feature summaries.
- Displayed numerical and categorical drift results.
- Added tests for dashboard data helpers.
- No production monitoring, live alerts, database, cloud deployment or authentication added.

## Previous Stage 8A Completion

- Added local drift detection utilities for prediction logs.
- Added deterministic simulated current batch generation.
- Added numerical and categorical drift checks.
- Generated drift detection JSON and Markdown reports.
- Added tests for drift detection utilities.
- No Streamlit dashboard, production monitoring, live alerts, database or cloud deployment added yet.

## Previous Stage 7B Completion

- Added script to send synthetic Telco payloads to the local `/predict` endpoint.
- Generated sample prediction events through the API logging workflow.
- Added summary report for sample prediction traffic.
- Kept generated prediction logs excluded from Git.
- No drift detection, dashboard, database, cloud deployment or production monitoring added yet.

## Previous Stage 7A Completion

- Added local JSONL prediction logging for successful `/predict` calls.
- Logged prediction timestamp, request ID, churn probability, predicted class, risk label and selected monitoring features.
- Added tests for the logging helper and `/predict` logging behaviour.
- Kept prediction logs excluded from Git.
- No drift detection, dashboard, database, cloud deployment or production monitoring added yet.

## Previous Stage 6A Completion

- Added local MLflow tracking to the training script.
- Logged training parameters.
- Logged LogisticRegression metrics.
- Logged DummyClassifier baseline metrics.
- Logged model artifact and training metrics report as MLflow artifacts.
- Kept `mlruns/` excluded from Git.
- No MLflow server, model registry, prediction logging, drift detection or dashboard added yet.

## Previous Stage 5B Completion

- Added GitHub Actions CI workflow.
- CI installs Python dependencies from `requirements.txt`.
- CI runs `python -m pytest` on push and pull request.
- CI does not require the raw dataset or model artifact.
- No Docker build, MLflow, dashboard, prediction logging or drift detection added yet.

## Previous Stage 5A Completion

- Added Dockerfile for the FastAPI API.
- Added `.dockerignore`.
- Docker image runs the FastAPI app on port 8000.
- Docker image loads the local model pipeline artifact.
- Raw dataset is excluded from the Docker build context.
- Docker image includes project-root markers needed by the path helper without copying the raw dataset.
- No Docker Compose, CI, MLflow, dashboard, prediction logging or drift detection added yet.

## Previous Stage 4B Completion

- Added pytest tests for GET `/health`.
- Added pytest tests for successful POST `/predict` using mocked model pipeline.
- Added pytest tests for missing model artifact behaviour.
- Added pytest tests for invalid prediction payload validation.
- Tests do not require raw dataset or real model artifact.
- Preserved scope by not adding Docker, CI, MLflow, dashboard, prediction logging or drift detection yet.

## Previous Stage 4A Completion

- Added FastAPI app.
- Added `/health` endpoint.
- Added `/predict` endpoint.
- Added Pydantic request and response schemas.
- API loads the saved local model pipeline artifact.
- API does not retrain the model.

## Previous Stage 3C Completion

- Added pytest tests for Telco data cleaning.
- Added pytest tests for preprocessing pipeline construction.
- Added pytest tests for baseline model pipeline fit/predict behaviour.
- Tests use synthetic data and do not require the raw dataset.
- Preserved scope by not adding API, Docker, CI, MLflow, dashboard, prediction logging or drift detection yet.

## Previous Stage 3B Completion

- Added command-line training script `src/models/train.py`.
- Added command-line evaluation script `src/models/evaluate.py`.
- Updated the local model artifact path to `artifacts/model_pipeline.joblib`.
- Generated local model pipeline artifact.
- Generated `reports/training_metrics.json` with real local metrics.
- Generated `reports/evaluation_summary.md` with real local metrics.
- Preserved scope by not adding API, Docker, CI, MLflow, dashboard, prediction logging or drift detection yet.

## Previous Stage 3A Completion

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

Stage 10A: finalise model card and risk register.

## Known Risks

- The public dataset is small and may not represent real customer populations.
- Future simulated production traffic may not reflect real production data.
- Churn probability can be misused if treated as an automatic customer treatment decision.
- Drift monitoring in this portfolio project will be simulated rather than based on live production data.
- Scope could expand too quickly if cloud deployment, Kubernetes or streaming systems are added too early.
- Baseline metrics may change if the dataset version or preprocessing assumptions change.

## Current Status Summary

The project README now documents the full local MLOps workflow, architecture, reproducibility steps, evidence artifacts and safe portfolio claims. The project remains a local prototype with no production deployment, live monitoring, database, cloud infrastructure or authentication code added.

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
- 2026-06-29: Added command-line training and evaluation scripts for Stage 3B.
- 2026-07-03: Added synthetic-data pytest coverage for Stage 3C.
- 2026-07-04: Added FastAPI health and prediction endpoints for Stage 4A.
- 2026-07-04: Added FastAPI endpoint tests for Stage 4B.
- 2026-07-04: Added Dockerfile and `.dockerignore` for Stage 5A local API containerisation.
- 2026-07-05: Added GitHub Actions pytest workflow for Stage 5B.
- 2026-07-06: Added local MLflow experiment tracking to the training workflow for Stage 6A.
- 2026-07-07: Added local JSONL prediction logging for Stage 7A.
- 2026-07-07: Added synthetic local prediction traffic generation for Stage 7B.
- 2026-07-07: Added simulated drift detection using local prediction logs for Stage 8A.
- 2026-07-08: Added local Streamlit monitoring dashboard MVP for Stage 9A.
- 2026-07-08: Polished README workflow and added project evidence summary for Stage 9B.
