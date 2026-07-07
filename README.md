# MLOps Customer Churn Prediction & Drift Monitoring Platform

## Short Overview

This project turns a notebook-based customer churn prediction baseline into a reproducible, testable, containerised and monitored ML service prototype. It is designed as a portfolio-grade MLOps project that shows how an experimentation-stage machine learning workflow can be moved toward production-style engineering practices.

The project is a local prototype, not a real production deployment. It will avoid claims of real business impact, real company deployment or real customer retention improvement.

## Project Architecture

The local workflow follows this path:

```text
Raw Telco CSV
-> training pipeline
-> saved model artifact
-> FastAPI inference service
-> prediction logs
-> simulated drift detection
-> Streamlit dashboard
```

MLflow records local training experiment metadata under `mlruns/`. GitHub Actions runs the pytest suite automatically on push and pull request. Docker packages the local FastAPI API service using the locally generated model artifact. This is a local MLOps prototype, not a production deployment.

## Reproducibility Workflow

From the project root:

1. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

2. Add the raw Telco CSV:

```text
data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv
```

3. Run tests:

```bash
python -m pytest
```

4. Train the model:

```bash
python -m src.models.train
```

5. Evaluate the model:

```bash
python -m src.models.evaluate
```

6. Start the API:

```bash
python -m uvicorn app.main:app --reload
```

7. Generate sample prediction traffic:

```bash
python -m scripts.generate_sample_prediction_traffic --n 30
```

8. Run simulated drift detection:

```bash
python -m scripts.run_simulated_drift_detection
```

9. Start the dashboard:

```bash
python -m streamlit run dashboard/streamlit_app.py
```

10. Optionally run the local API with Docker:

```bash
docker build -t mlops-customer-churn-api .
docker run --rm -p 8000:8000 mlops-customer-churn-api
```

## Real-World Problem Framing

Customer churn prediction is a common machine learning problem in subscription-based businesses such as telecom, SaaS, streaming services and membership platforms. These businesses often want to identify customers who may stop using the service so that support, retention or account teams can review the situation.

A model evaluated only in a notebook is not enough for this type of workflow. In a realistic setting, the model also needs to be reproducible, testable, deployable behind an API and monitorable over time. Input data can change, prediction behaviour can drift and engineering failures can affect how the model is used. This project focuses on demonstrating those MLOps concerns around a churn prediction use case.

## Dataset Choice

The project will use the Telco Customer Churn dataset. The target variable is `Churn`.

The dataset contains customer demographics, service subscription information, account information and billing-related features. The dataset file will not be included in this repository. Raw and processed data folders are included only as placeholders so the project structure is clear.

## Data Setup

1. Download the Telco Customer Churn CSV.
2. Keep the filename as `WA_Fn-UseC_-Telco-Customer-Churn.csv`.
3. Place it at `data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv`.
4. The dataset is intentionally not committed to the repository.

## Prediction Task

The prediction task is binary classification.

Input: customer profile, service and billing features.

Output: churn probability and a churn risk label.

The churn probability will represent the model-estimated likelihood that a customer belongs to the churn class. The risk label will be derived from that probability in a later stage of the project.

## Why This Dataset Is Suitable for an MLOps Portfolio Project

The Telco Customer Churn dataset is suitable for this MLOps prototype because it supports both machine learning experimentation and production-style engineering work.

- Its tabular structure is suitable for scikit-learn pipelines.
- Categorical and numerical features require preprocessing.
- Customer-level prediction is suitable for API serving.
- Incoming customer profiles can be used to simulate production prediction traffic.
- Features such as `tenure`, `MonthlyCharges` and `Contract` are suitable for simulated drift monitoring.

## Baseline Definition

The initial baseline will be a reasonable notebook/script-based experimentation workflow. It is not intended to be weak or fake. It represents the type of prototype that might exist before MLOps practices are added.

The baseline will include:

- manual data loading
- preprocessing and model training in a notebook or script
- held-out test evaluation
- manual model saving

The baseline will not include:

- API serving
- Docker packaging
- automated tests
- CI
- prediction logging
- drift monitoring


## Baseline Experiment

The Stage 2 baseline notebook is available at `notebooks/01_baseline_experiment.ipynb`. When run with the local Telco Customer Churn CSV, it trains a `DummyClassifier` sanity-check baseline and a simple `LogisticRegression` baseline using pandas and scikit-learn.

The generated baseline summary is available at `reports/baseline_summary.md` after a successful local notebook run.


## Reproducible Training and Evaluation

The exploratory baseline remains in `notebooks/01_baseline_experiment.ipynb`. Reusable workflow code lives under `src/` and can be run from the command line after the dataset is placed at `data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv`.

Train the baseline pipeline:

```bash
python -m src.models.train
```

Evaluate the saved pipeline:

```bash
python -m src.models.evaluate
```

The training script generates `artifacts/model_pipeline.joblib` locally. This artifact stores the full scikit-learn preprocessing and LogisticRegression pipeline and is intentionally excluded from Git. The evaluation script loads the saved pipeline and evaluates it on the same fixed held-out split used by the baseline workflow.

## MLflow Experiment Tracking

Training runs log parameters, metrics and local artifacts to MLflow.

Run training from the project root:

```bash
python -m src.models.train
```

This project uses local file-based MLflow tracking under `mlruns/`. Start the local MLflow UI from the project root with the command for your shell.

Windows CMD:

```cmd
set "MLFLOW_ALLOW_FILE_STORE=true" && python -m mlflow ui --backend-store-uri ./mlruns
```

macOS/Linux:

```bash
MLFLOW_ALLOW_FILE_STORE=true python -m mlflow ui --backend-store-uri ./mlruns
```

Open:

```text
http://127.0.0.1:5000
```

`mlruns/` is excluded from Git. This remains local experiment tracking, not a remote tracking server or model registry.

## Tests

From the project root, run:

```bash
python -m pytest
```

The tests include data cleaning, preprocessing, model-pipeline and FastAPI endpoint checks. They use small synthetic inputs and mocked model loading where appropriate, so they do not require the raw Telco CSV file or a committed model artifact.

## Continuous Integration

GitHub Actions runs the pytest suite on every push and pull request using Python 3.10.

The CI workflow installs dependencies from `requirements.txt` and runs `python -m pytest`. These tests use synthetic data and mocked API model loading where appropriate, so CI does not require the raw Telco CSV file or a committed `artifacts/model_pipeline.joblib` file.

## Run the FastAPI App

From the project root, first generate the local model artifact:

```bash
python -m src.models.train
```

Then start the API:

```bash
python -m uvicorn app.main:app --reload
```

The API loads `artifacts/model_pipeline.joblib`. The artifact is generated locally and excluded from Git. OpenAPI docs are available at:

```text
http://127.0.0.1:8000/docs
```

Use `POST /predict` with a Telco customer JSON payload:

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

## Prediction Logging

Each successful `POST /predict` call appends one JSONL event to `logs/predictions.jsonl`.

Prediction log events include a UTC timestamp, request ID, model artifact path, churn probability, predicted class, risk label and selected monitoring features: `tenure`, `MonthlyCharges`, `TotalCharges`, `Contract`, `InternetService` and `PaymentMethod`.

`logs/predictions.jsonl` is excluded from Git. These local logs are intended for later simulated drift detection and dashboarding. This is local prototype logging, not production observability.

## Generate Sample Prediction Traffic

From the project root, train the model first:

```bash
python -m src.models.train
```

Start the FastAPI app:

```bash
python -m uvicorn app.main:app --reload
```

In a second terminal, generate synthetic local sample traffic:

```bash
python -m scripts.generate_sample_prediction_traffic --n 30
```

Prediction events are appended to `logs/predictions.jsonl`, and a summary is written to `reports/sample_prediction_traffic_summary.md`.

`logs/predictions.jsonl` is excluded from Git. The generated traffic is synthetic local sample traffic intended to support later simulated drift detection and dashboarding. It is not real production traffic.

## Simulated Drift Detection

Generate prediction logs first:

```bash
python -m scripts.generate_sample_prediction_traffic --n 30
```

Run simulated drift detection:

```bash
python -m scripts.run_simulated_drift_detection
```

Outputs:

```text
reports/drift_detection_results.json
reports/drift_detection_summary.md
```

This workflow uses local prediction logs from `logs/predictions.jsonl`. The current batch is simulated by applying controlled feature shifts, so this is for local MLOps portfolio demonstration and is not real production drift monitoring. `logs/predictions.jsonl` remains excluded from Git.

## Streamlit Monitoring Dashboard

Run the local dashboard workflow from the project root:

1. Train the model:

```bash
python -m src.models.train
```

2. Start the FastAPI app:

```bash
python -m uvicorn app.main:app --reload
```

3. In a second terminal, generate sample prediction traffic:

```bash
python -m scripts.generate_sample_prediction_traffic --n 30
```

4. Run simulated drift detection:

```bash
python -m scripts.run_simulated_drift_detection
```

5. Start the dashboard:

```bash
python -m streamlit run dashboard/streamlit_app.py
```

Open the local Streamlit URL shown in the terminal.

The dashboard reads `logs/predictions.jsonl` and `reports/drift_detection_results.json`. `logs/predictions.jsonl` is excluded from Git. The dashboard is a local prototype, not production monitoring or live alerting.

## Run with Docker

From the project root, generate the local model artifact:

```bash
python -m src.models.train
```

Build the Docker image:

```bash
docker build -t mlops-customer-churn-api .
```

Run the container:

```bash
docker run --rm -p 8000:8000 mlops-customer-churn-api
```

Open:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

The Docker image uses the locally generated `artifacts/model_pipeline.joblib`. The raw dataset is not copied into the image. The Dockerfile does not train the model. This is a local containerised API prototype, not a cloud deployment.

## Planned MLOps Components

The planned MLOps components are:

- FastAPI prediction endpoint
- Pydantic input validation
- Docker
- pytest
- GitHub Actions CI
- MLflow tracking
- prediction logging
- synthetic drift detection
- Streamlit monitoring dashboard
- model card
- risk register

## Planned Evaluation

### Model Evaluation

Model performance will be evaluated on held-out test data using:

- ROC-AUC
- F1
- precision
- recall
- confusion matrix

Baseline model metrics are generated from a local notebook run and summarised in `reports/baseline_summary.md`.

### Engineering and MLOps Evaluation

Engineering and MLOps quality will be evaluated using local benchmarking, tests and generated project evidence such as:

- API average latency
- API p95 latency
- number of pytest tests
- CI pass/fail status
- number of MLflow experiment runs
- prediction log generation
- drift detection output under simulated feature shifts

## Project Evidence

Generated evidence files:

- `reports/baseline_summary.md`
- `reports/training_metrics.json`
- `reports/evaluation_summary.md`
- `reports/mlflow_run_summary.md`
- `reports/sample_prediction_traffic_summary.md`
- `reports/drift_detection_results.json`
- `reports/drift_detection_summary.md`
- `reports/project_evidence_summary.md`

Additional local evidence to capture manually:

- GitHub Actions green run screenshot
- MLflow UI screenshot
- FastAPI `/docs` screenshot
- Streamlit dashboard screenshot
- Docker build/run terminal output

## What This Project Demonstrates

- Reproducible model training and evaluation with a saved scikit-learn pipeline.
- Testable data cleaning, preprocessing, model-pipeline and API behaviour.
- FastAPI model serving with Pydantic request validation.
- Dockerised local API serving.
- GitHub Actions CI running `python -m pytest`.
- Local MLflow experiment tracking.
- Local JSONL prediction logging.
- Synthetic sample prediction traffic generation.
- Simulated drift detection from local prediction logs.
- Local Streamlit monitoring dashboard for prediction and drift evidence.

## Out-of-Scope Items for MVP

The MVP will not include:

- real cloud deployment
- Kubernetes
- complex database architecture
- real-time streaming infrastructure
- user authentication
- enterprise monitoring stack
- claims of real business impact

## Limitations and Responsible Use Notes

The Telco Customer Churn dataset is small and public, so results from this project should not be treated as evidence of real production performance. The project does not use real customer data, real production traffic or cloud infrastructure.

There is no real production deployment, live production monitoring, validated business retention policy or automated customer treatment workflow. Model predictions should support human review rather than automatically decide customer treatment. False positives and false negatives have different business implications. For example, a false positive could lead to unnecessary retention action, while a false negative could miss a customer who may churn.

Prediction traffic is synthetic local sample traffic. Drift detection is simulated, uses simple demonstration thresholds and does not use ground-truth labels. The Streamlit dashboard is a local prototype for portfolio evidence, not production observability or live alerting.

## Development Roadmap

- Stage 1: repository setup and dataset decision
- Stage 2: baseline notebook and initial metrics
- Stage 3: refactor training and evaluation into `src`
- Stage 4: FastAPI prediction service
- Stage 5: tests, Docker and CI
- Stage 6: MLflow tracking
- Stage 7: prediction logging and drift detection
- Stage 8: Streamlit dashboard
- Stage 9: model card, risk register and README polish
