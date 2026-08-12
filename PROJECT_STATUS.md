# Project Status

## Current Phase

Stage 11.5E manual end-to-end GitHub Actions deployment validated successfully.

## Stage 11.5 Status

- Stage 11.5A: user-assigned managed identity `id-github-mlops-churn` completed.
- Stage 11.5B: GitHub-to-Azure OIDC federation restricted to this repository's `main` branch completed.
- Stage 11.5C: resource-scoped Azure RBAC completed with narrowly scoped registry and Container Apps permissions.
- Stage 11.5D: real OIDC login and Azure read-access smoke test completed.
- Stage 11.5E: manual end-to-end deployment through `.github/workflows/azure-deploy.yml` validated successfully.
- Stage 11.5 remains open until automatic deployment from `main` is enabled and validated.

## Stage 11.5E Validation

- Manually dispatched the deployment workflow from `main` at source commit `b613f29250c3b4c14b54a4c5a7a7a39579effaca`.
- Ran 34 tests successfully on the GitHub-hosted runner.
- Retrieved `model_pipeline.joblib` from the pinned GitHub Release and verified its authoritative SHA-256 before Docker build; the workflow did not train the model.
- Built and pushed only immutable image `acrmlopschurnkl5685752-ddhkccgxcecpfjb6.azurecr.io/mlops-churn-api:b613f29250c3`.
- Recorded pushed digest `sha256:10d9aab1516f80e0c54edd05cb6410efb7d8a7a341c85ee7270b97f3aaa1805a`.
- Updated the existing Container App from image tag `fcd471855395` to `b613f29250c3`, then independently queried Azure and confirmed the configured image matched.
- Used OIDC federated authentication without long-lived Azure client secrets and a temporary masked ACR token without enabling the ACR admin account.
- The bounded post-deployment `/health` check accommodated revision startup and passed on attempt 2 with `status: ok` and `model_artifact_exists: true`; the first timeout was not treated as an outage.
- The workflow remains `workflow_dispatch` only. Automatic deployment from `main` is not yet implemented.

## Stage 11.2 Completion

- Created the Basic Azure Container Registry `acrmlopschurnkl5685752` in Sweden Central.
- Manually pushed the locally validated image to repository `mlops-churn-api` with tag `fcd471855395`.
- Verified the image through Azure CLI repository, tag and digest queries.
- Recorded registry manifest digest `sha256:db8466a6f629f6fbb3cd270b2b917fd00b7c77d18a8df56d455c5ff634100dde`.

## Stage 11.3 Completion

- Created Container Apps environment `cae-mlops-churn` and Container App `ca-mlops-churn-api` in Sweden Central.
- Used the Consumption workload profile with `0.5 vCPU / 1 GiB`, external HTTPS ingress and target port 8000.
- Configured managed identity for registry authentication.
- Confirmed the cloud-hosted portfolio API reached Running state.
- Validated `GET /health`, including `status: ok` and `model_artifact_exists: true`.
- Validated `POST /predict` with a synthetic request; the cloud result matched the previously validated local Docker prediction.
- Confirmed `GET /docs` returned HTTP 200.

## Stage 11.4 Completion

- Validated live Azure Container Apps system logs for image pull, container creation and container startup.
- Validated live console logs for Uvicorn startup and successful `/health`, `/predict` and `/docs` requests.
- Validated persistent Log Analytics queries using `ContainerAppConsoleLogs_CL` and `ContainerAppSystemLogs_CL` in `log-mlops-churn`.
- Observed a startup probe warning followed by successful startup and endpoint requests; it was not treated as an outage.
- Observed the Consumption app scale its replica down after inactivity without making stronger cost or availability claims.
- These stages are manual deployment validation for a cloud-hosted portfolio deployment, not production traffic or a production SLA.
- This documentation sync created no Azure resources, OIDC configuration, deployment workflow, alert, dashboard or Application Insights resource.

## Previous Stage 11.1 Completion

- Added a machine-readable deployment artifact manifest with validated provenance, metrics, compatibility versions and authoritative SHA-256 checksum.
- Added a standard-library retrieval script for a future pinned GitHub Release asset.
- The retrieval path downloads to a temporary file and installs the artifact only after SHA-256 verification.
- Pinned scikit-learn 1.7.2 and joblib 1.5.3 for compatibility with the validated deployment artifact.
- Added offline tests for manifest loading, release URL construction, checksum verification and mismatch rejection.
- Recorded the published `model-v1.0.0` release and its `model_pipeline.joblib` asset.
- Confirmed that GitHub reports the same SHA-256 as the authoritative deployment manifest.
- Real clean-runner/network retrieval was identified as the next artifact validation step at that stage.
- No Azure runtime or workload resource or deployment workflow was created by the model release step.

## Previous Stage 11.0 Completion

- Documented the Stage 11 Azure deployment plan, resource naming convention, cost guardrails and security constraints.
- Documented an unchecked teardown checklist for use after future cloud MVP evidence collection.
- Selected Azure Container Registry and Azure Container Apps as the intended cloud MVP direction in UK South.
- Recorded GitHub OIDC federation and narrowly scoped resource-group permissions as requirements for future deployment automation.
- Confirmed that `rg-mlops-churn-portfolio` has been created in UK South.
- No Azure deployment code or deployment workflow has been added, and no cloud runtime or workload resources such as ACR, Container Apps, Log Analytics or the deployment identity have been provisioned yet.

## Local MLOps Workflow Completion

- The local workflow from baseline experimentation through reusable training and evaluation, API serving, tests, Docker packaging, pytest CI, MLflow tracking, prediction logging, simulated drift monitoring, dashboarding, documentation and local API latency benchmarking is complete.
- Local evidence remains portfolio MVP evidence and does not represent production traffic, a production SLA or real customer impact.

## Previous Stage 10B Completion

- Added a local synthetic API latency benchmark script for the FastAPI `/predict` endpoint.
- The benchmark sends sequential synthetic Telco-like requests and reports average, p50, p95, minimum and maximum latency.
- The benchmark counts successful and failed requests and reports success rate.
- Benchmark output is written to `reports/api_latency_benchmark.json` and `reports/api_latency_benchmark.md`.
- Clarified that the benchmark is local synthetic evidence, not a production performance test or production deployment.

## Previous Stage 10A Completion

- Finalised model card with intended use, metrics, inputs/outputs, monitoring notes and limitations.
- Finalised risk register covering model performance, governance, monitoring, data validity, privacy and communication risks.
- Clarified that the project remains a local MLOps prototype, not production deployment.
- No new model, API, dashboard, Docker or CI functionality added.

## Previous Stage 9B Completion

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

Enable and validate automatic deployment from `main` using the already validated deployment workflow. Pull request workflows must remain non-deploying.

## Known Risks

- The public dataset is small and may not represent real customer populations.
- Future simulated production traffic may not reflect real production data.
- Churn probability can be misused if treated as an automatic customer treatment decision.
- Drift monitoring in this portfolio project will be simulated rather than based on live production data.
- Scope could expand too quickly if cloud deployment, Kubernetes or streaming systems are added too early.
- Baseline metrics may change if the dataset version or preprocessing assumptions change.
- The deployment workflow currently requires manual dispatch; automatic deployment from `main` has not yet been validated.
- A non-blocking Azure CLI version-parsing warning was observed in the successful run and did not prevent login, image push, deployment verification or health validation.

## Current Status Summary

The local MLOps workflow is complete. Stages 11.2 through 11.4 validated ACR, the cloud-hosted portfolio API and Log Analytics evidence. Stage 11.5 has now validated GitHub OIDC federation without long-lived Azure client secrets, resource-scoped RBAC and a manually dispatched end-to-end deployment using an immutable Git-SHA image. Stage 11.5 remains open because automatic deployment from `main` has not yet been enabled or validated.

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
- Azure Container Registry repository, tag and digest evidence.
- Azure-hosted `/health`, synthetic `/predict` and `/docs` validation evidence.
- Azure Container Apps live and persistent Log Analytics query evidence.
- GitHub Actions OIDC smoke-test evidence.
- Manual deployment run evidence for artifact verification, immutable image push, deployed-image confirmation and the successful bounded `/health` check.

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
- 2026-07-08: Finalised model card and risk register for Stage 10A.
- 2026-07-11: Added local synthetic API latency benchmarking evidence for Stage 10B.
- 2026-08-12: Documented Azure deployment guardrails and teardown planning for Stage 11.0 after creating `rg-mlops-churn-portfolio` in UK South; no cloud runtime or workload resources were provisioned.
- 2026-08-12: Added the Stage 11.1B-2 deployment artifact manifest, compatibility pins and offline checksum-verification foundation.
- 2026-08-12: Published the validated `model_pipeline.joblib` asset in the `model-v1.0.0` release; GitHub reported the manifest-matching SHA-256, while real remote retrieval remains pending.
- 2026-08-13: Completed Stage 11.2 manual ACR image push and digest validation in Sweden Central.
- 2026-08-13: Completed Stage 11.3 manual Azure Container Apps deployment and synthetic endpoint validation.
- 2026-08-13: Completed Stage 11.4 live and persistent Azure Container Apps log validation through Log Analytics.
- 2026-08-13: Completed Stage 11.5A through 11.5D identity, federation, resource-scoped RBAC and real OIDC smoke validation.
- 2026-08-13: Validated the Stage 11.5E manual end-to-end GitHub Actions deployment of immutable image tag `b613f29250c3`, including post-deployment image and health checks.
