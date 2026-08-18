# MLOps Workflow

This document contains the detailed local reproducibility and GitHub Actions workflow. Run local commands from the repository root.

## Local Prerequisites

- Python 3.10
- Docker for container validation
- The Telco CSV for local training and evaluation

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Place the raw dataset at:

```text
data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv
```

The raw dataset is excluded from Git.

## Tests

```bash
python -m pytest
```

The current suite contains 42 tests. Tests use small synthetic fixtures and mocked model loading where appropriate, so pytest does not require the raw CSV or a committed model artifact.

## Train and Evaluate

Train the full preprocessing and `LogisticRegression` pipeline:

```bash
python -m src.models.train
```

This writes:

```text
artifacts/model_pipeline.joblib
reports/training_metrics.json
reports/mlflow_run_summary.md
```

Evaluate the saved pipeline on the fixed held-out split:

```bash
python -m src.models.evaluate
```

This writes `reports/evaluation_summary.md`. Evaluation loads the saved pipeline rather than silently retraining it.

## Local MLflow Tracking

Training records parameters, model metrics and local artifacts under the Git-ignored `mlruns/` directory. This is local file-based experiment tracking, not a remote tracking server or model registry.

Start the UI from the repository root.

Windows CMD:

```cmd
set "MLFLOW_ALLOW_FILE_STORE=true" && python -m mlflow ui --backend-store-uri ./mlruns
```

macOS/Linux:

```bash
MLFLOW_ALLOW_FILE_STORE=true python -m mlflow ui --backend-store-uri ./mlruns
```

Open `http://127.0.0.1:5000`.

## Retrieve the Published Deployment Artifact

A clean environment can retrieve the pinned `model-v1.0.0` release asset instead of training:

```bash
python -m scripts.fetch_model_artifact
```

The script reads `deployment/model_artifact.json`, downloads to a temporary location, verifies the authoritative SHA-256 and only then installs the file at `artifacts/model_pipeline.joblib`. It does not deserialize the artifact during retrieval.

Use only an artifact whose provenance and checksum have been verified. Joblib/pickle files can execute code during deserialization and must not be loaded from an untrusted source.

## Run the FastAPI Service

Create the local artifact by training or verified retrieval, then start the API:

```bash
python -m uvicorn app.main:app --reload
```

Endpoints:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/predict
```

Example synthetic request body for `POST /predict`:

```json
{
  "gender": "Female",
  "SeniorCitizen": 0,
  "Partner": "Yes",
  "Dependents": "No",
  "tenure": 12,
  "PhoneService": "Yes",
  "MultipleLines": "No",
  "InternetService": "DSL",
  "OnlineSecurity": "Yes",
  "OnlineBackup": "No",
  "DeviceProtection": "No",
  "TechSupport": "No",
  "StreamingTV": "No",
  "StreamingMovies": "No",
  "Contract": "Month-to-month",
  "PaperlessBilling": "Yes",
  "PaymentMethod": "Electronic check",
  "MonthlyCharges": 59.9,
  "TotalCharges": 718.8
}
```

Successful responses contain `churn_probability`, `churn_prediction` and `risk_label`.

## Run with Docker

The Docker build requires a locally trained or verified release artifact at `artifacts/model_pipeline.joblib`. The Dockerfile does not train the model, and the raw CSV is not copied into the image.

```bash
docker build -t mlops-customer-churn-api .
docker run --rm -p 8000:8000 mlops-customer-churn-api
```

Validate `http://127.0.0.1:8000/health` and `http://127.0.0.1:8000/docs`.

## Local API Benchmark

With the API already running:

```bash
python -m scripts.benchmark_api_latency --n 100
```

Results are written to `reports/api_latency_benchmark.json` and `reports/api_latency_benchmark.md`. This is a sequential synthetic local benchmark, not a production performance test.

## GitHub Actions CI

The [CI workflow](../.github/workflows/ci.yml) runs dependency installation and `python -m pytest` on pushes and pull requests.

For pull requests only, it also:

1. retrieves the pinned release artifact;
2. verifies SHA-256 through the repository retrieval script;
3. confirms the artifact exists; and
4. validates the Docker build.

The pull-request workflow does not authenticate to Azure, push an image or deploy.

## GitHub Actions Azure Deployment

The [Azure deployment workflow](../.github/workflows/azure-deploy.yml) supports manual dispatch and deployment-relevant pushes to `main`. Documentation-only and test-only paths do not trigger this deployment workflow.

The validated sequence is:

```text
pytest
-> verified artifact retrieval
-> Docker build
-> Azure OIDC login
-> temporary ACR authentication
-> immutable Git-SHA image push
-> Container Apps image update
-> deployed-image verification
-> bounded HTTPS /health validation
```

GitHub Actions uses OIDC federation and resource-scoped RBAC. It does not use a long-lived Azure client secret, `AZURE_CREDENTIALS`, an ACR admin user or committed Azure credentials.

The workflow updates the existing cloud application; infrastructure provisioning and teardown remain separate concerns documented in the [Azure deployment plan](azure_deployment_plan.md) and [teardown checklist](azure_teardown_checklist.md).

## Generated and Excluded Outputs

The following runtime or generated outputs remain outside Git:

- `data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv`;
- `artifacts/model_pipeline.joblib`;
- `mlruns/`; and
- `logs/predictions.jsonl`.

Committed reports and the deployment manifest provide the repository evidence without committing raw data, local logs or generated binary model files.
