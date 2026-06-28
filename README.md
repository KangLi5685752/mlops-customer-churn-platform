# MLOps Customer Churn Prediction & Drift Monitoring Platform

## Short Overview

This project turns a notebook-based customer churn prediction baseline into a reproducible, testable, containerised and monitored ML service prototype. It is designed as a portfolio-grade MLOps project that shows how an experimentation-stage machine learning workflow can be moved toward production-style engineering practices.

The project is a local prototype, not a real production deployment. It will avoid claims of real business impact, real company deployment or real customer retention improvement.

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

The Telco Customer Churn dataset is small and public, so results from this project should not be treated as evidence of real production performance. Simulated production traffic is useful for demonstrating engineering workflows, but it is not the same as real production traffic.

Model predictions should support human review rather than automatically decide customer treatment. False positives and false negatives have different business implications. For example, a false positive could lead to unnecessary retention action, while a false negative could miss a customer who may churn. Drift monitoring in this project will be simulated and should be interpreted as a portfolio demonstration rather than a complete production monitoring system.

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
