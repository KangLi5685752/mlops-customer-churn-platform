# Project Status

## Current Phase

MVP scope and dataset definition.

## Completed in This Step

- Created initial repository folder structure.
- Added placeholders for raw data, processed data, notebooks, source modules, app, dashboard and tests.
- Documented the project goal, business framing and dataset choice.
- Defined the baseline scope and planned MLOps components.
- Added a decision log.
- Added model card and risk register templates.
- Added minimal planned dependencies.
- Added `.gitignore` rules for local artifacts, data files, model files, logs and development files.

## Next Planned Task

Create the baseline notebook or script for the Telco Customer Churn dataset, including data loading instructions, preprocessing, train/test split, model training and initial held-out evaluation metrics.

## Known Risks

- The public dataset is small and may not represent real customer populations.
- Future simulated production traffic may not reflect real production data.
- Churn probability can be misused if treated as an automatic customer treatment decision.
- Drift monitoring in this portfolio project will be simulated rather than based on live production data.
- Scope could expand too quickly if cloud deployment, Kubernetes or streaming systems are added too early.

## Current Status Summary

The project has been initialized as a portfolio-grade MLOps prototype for Telco customer churn prediction. The current repository state defines the MVP boundary, dataset decision, planned engineering components and responsible-use framing. No model, API, Docker, CI, MLflow or dashboard implementation has been added yet.

## Evidence to Collect Later for CV / README / LinkedIn

- Held-out model evaluation metrics.
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
