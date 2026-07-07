# Project Evidence Summary

## Project Title

MLOps Customer Churn Prediction & Drift Monitoring Platform

## Completed Stages

- Baseline notebook experiment with Telco churn data.
- Reusable training and evaluation pipeline under `src/`.
- Pytest coverage for data processing, model pipeline, API, logging, drift and dashboard helpers.
- FastAPI `/health` and `/predict` endpoints.
- Dockerfile for local API containerisation.
- GitHub Actions CI for pytest.
- Local MLflow experiment tracking.
- Local JSONL prediction logging.
- Synthetic sample prediction traffic generation.
- Simulated drift detection reports.
- Local Streamlit monitoring dashboard MVP.
- Final README and evidence documentation polish.

## Core Commands

```bash
python -m pip install -r requirements.txt
python -m pytest
python -m src.models.train
python -m src.models.evaluate
python -m uvicorn app.main:app --reload
python -m scripts.generate_sample_prediction_traffic --n 30
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
- `reports/drift_detection_results.json`
- `reports/drift_detection_summary.md`
- `reports/project_evidence_summary.md`

## Local Evidence to Capture Manually

- GitHub Actions green run screenshot.
- MLflow UI screenshot.
- FastAPI `/docs` screenshot.
- Streamlit dashboard screenshot.
- Docker build and run terminal output.

## Safe Portfolio Wording Examples

- Built a local MLOps prototype for customer churn prediction using scikit-learn, FastAPI, Docker, GitHub Actions and Streamlit.
- Containerised a FastAPI model-serving app for local inference.
- Added GitHub Actions CI to run pytest on push and pull request.
- Implemented local prediction logging and simulated drift detection from generated inference traffic.
- Created a local dashboard prototype for prediction-log and simulated-drift evidence.

## Unsafe Wording to Avoid

- Deployed to production.
- Improved real customer retention.
- Production monitoring.
- Real-time enterprise MLOps platform.
- Real customer data pipeline.
- Validated business retention policy.
