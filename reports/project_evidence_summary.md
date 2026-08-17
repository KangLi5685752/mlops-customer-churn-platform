# Project Evidence Summary

## Project Title

MLOps Customer Churn Prediction & Drift Monitoring Platform

## Completed Evidence

### Machine Learning

- Reusable training and evaluation pipeline under `src/` using a full scikit-learn preprocessing and `LogisticRegression` pipeline.
- Held-out `LogisticRegression` ROC-AUC of `0.8419`, compared with `0.5000` for the `DummyClassifier` sanity-check baseline.

### Serving and Packaging

- FastAPI `GET /health` and `POST /predict` endpoints with Pydantic request validation.
- Docker packaging of the inference service without training the model inside the image.

### Testing and Experiment Tracking

- Current pytest suite: 42 passing tests covering data processing, model pipelines, API behaviour, artifact retrieval, logging, drift, dashboards and latency helpers.
- Local file-based MLflow experiment tracking under the Git-ignored `mlruns/` directory.

### Monitoring

- Local JSONL prediction logging and synthetic prediction traffic generation.
- Simulated drift detection with generated JSON and Markdown evidence.
- Local Streamlit dashboard for prediction-log and simulated-drift evidence.

### Artifact Delivery

- Published GitHub Release `model-v1.0.0` with the `model_pipeline.joblib` asset.
- Pinned deployment metadata and authoritative SHA-256 in `deployment/model_artifact.json`.
- Artifact retrieval downloads to a temporary location and verifies SHA-256 before installation or use.

### Azure Deployment and Observability

- Azure Container Registry image storage and Azure Container Apps hosting for the portfolio FastAPI service.
- Public HTTPS validation of `/health`, `/predict` with a synthetic request and `/docs`.
- Azure Container Apps runtime and lifecycle evidence validated through Azure Log Analytics.

### CI/CD

- Pull requests run pytest, retrieve and verify the pinned model artifact, and validate the Docker build without Azure authentication or deployment.
- Deployment-relevant pushes to `main` use GitHub Actions OIDC federation and resource-scoped Azure RBAC.
- Deployment uses immutable Git-SHA image tags, verifies the configured Container App image and runs a bounded post-deployment `/health` check.

### API Latency Evidence

- Local benchmark: 100/100 successful sequential synthetic requests with `12.205 ms` p95 latency.
- Azure-hosted benchmark: 100/100 successful sequential synthetic requests with `61.961 ms` p95 client-observed end-to-end latency.
- Hosted results are portfolio benchmark evidence, not production traffic, pure inference latency, a load test or an SLA measurement.

## Core Commands

```bash
python -m pip install -r requirements.txt
python -m pytest
python -m src.models.train
python -m src.models.evaluate
python -m scripts.fetch_model_artifact
python -m uvicorn app.main:app --reload
python -m scripts.generate_sample_prediction_traffic --n 30
python -m scripts.benchmark_api_latency --n 100
python -m scripts.run_simulated_drift_detection
python -m streamlit run dashboard/streamlit_app.py
docker build -t mlops-customer-churn-api .
docker run --rm -p 8000:8000 mlops-customer-churn-api
```

## Generated Reports

- `reports/baseline_summary.md`
- `reports/training_metrics.json`
- `reports/evaluation_summary.md`
- `reports/mlflow_run_summary.md`
- `reports/sample_prediction_traffic_summary.md`
- `reports/api_latency_benchmark.json`
- `reports/api_latency_benchmark.md`
- `reports/azure_api_latency_benchmark.json`
- `reports/azure_api_latency_benchmark.md`
- `reports/drift_detection_results.json`
- `reports/drift_detection_summary.md`
- `reports/model_card.md`
- `reports/risk_register.md`
- `reports/project_evidence_summary.md`

## Portfolio Screenshots to Capture

- Successful GitHub Actions deployment screenshot.
- Azure Container App status and revision screenshot.
- Azure Log Analytics query evidence screenshot.
- MLflow UI screenshot.
- FastAPI `/docs` and synthetic prediction screenshot.
- Streamlit dashboard screenshot.

## Safe Portfolio Wording Examples

- Built a portfolio ML engineering system using scikit-learn, FastAPI, Docker, GitHub Actions, Azure Container Apps and Streamlit.
- Deployed a containerised FastAPI ML inference service to Azure Container Apps through Azure Container Registry.
- Implemented GitHub Actions CI/CD using OIDC federation rather than a long-lived Azure client secret.
- Validated 100/100 hosted synthetic prediction requests at `61.961 ms` p95 client-observed end-to-end latency.
- Implemented local prediction logging, simulated drift monitoring and a local Streamlit dashboard.

## Unsafe Wording to Avoid

- Deployed to production.
- Production traffic or production SLA.
- Production drift monitoring.
- Enterprise-grade production platform.
- Improved real customer retention.
- Delivered real customer impact or retention uplift.
- Production monitoring.
- Real-time enterprise MLOps platform.
- Real customer data pipeline.
- Validated business retention policy.
