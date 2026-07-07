# Model Card: Telco Customer Churn Prediction

## Model Overview

- Project name: MLOps Customer Churn Prediction & Drift Monitoring Platform
- Task type: binary classification
- Target: `Churn`
- Positive class: `Churn = Yes`
- Model type: scikit-learn `LogisticRegression`
- Preprocessing: numeric imputation, numeric scaling and one-hot encoding for categorical features
- Artifact: `artifacts/model_pipeline.joblib`
- Serving interface: FastAPI `POST /predict`
- Monitoring support: local prediction logs, simulated drift detection and Streamlit dashboard

The saved artifact contains the full scikit-learn preprocessing and LogisticRegression pipeline.

## Intended Use

This model is intended for a local portfolio MLOps prototype. It demonstrates reproducible ML training, API serving, CI, Docker, local MLflow experiment tracking, prediction logging, simulated drift detection and dashboarding.

The model estimates customer churn risk as decision support. It should not automatically determine customer treatment.

## Not Intended For

- Real production deployment.
- Automatic customer retention decisions.
- Use with real customer data without further privacy, security, fairness and performance validation.
- Use as a validated business retention policy.
- High-stakes decision-making.

## Dataset

The project uses the public Telco Customer Churn dataset. The target variable is `Churn`.

The raw CSV is excluded from Git and expected locally at:

```text
data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv
```

Features include customer demographics, service subscription information, account information and billing-related variables. The dataset is public, small and static, so it may not represent real customer populations or current production behaviour.

## Training and Evaluation

The training workflow uses a fixed held-out test split. It trains a `DummyClassifier` sanity-check baseline and a LogisticRegression baseline.

| Model | ROC-AUC | Accuracy | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| DummyClassifier | 0.5000 | 0.7346 | 0.0000 | 0.0000 | 0.0000 |
| LogisticRegression | 0.8419 | 0.8055 | 0.6572 | 0.5588 | 0.6040 |

Metrics may vary if the dataset version, preprocessing assumptions or split configuration change.

## Model Performance Summary

The LogisticRegression model improves substantially over the DummyClassifier baseline in ROC-AUC and F1. Accuracy alone is not sufficient because churn is imbalanced.

Recall is moderate, so false negatives remain a concern: the model may miss customers who are likely to churn. Precision is also moderate, so false positives remain possible: the model may flag customers who would not have churned.

## Inputs and Outputs

Inputs are the 19 Telco customer features accepted by the API:

- `gender`
- `SeniorCitizen`
- `Partner`
- `Dependents`
- `tenure`
- `PhoneService`
- `MultipleLines`
- `InternetService`
- `OnlineSecurity`
- `OnlineBackup`
- `DeviceProtection`
- `TechSupport`
- `StreamingTV`
- `StreamingMovies`
- `Contract`
- `PaperlessBilling`
- `PaymentMethod`
- `MonthlyCharges`
- `TotalCharges`

The API does not accept `customerID`, and `Churn` is not available at prediction time.

Outputs:

- `churn_probability`
- `churn_prediction`
- `risk_label`

Risk label rule:

- `high`: probability >= 0.65
- `medium`: probability >= 0.35
- `low`: otherwise

This threshold rule is a local demonstration rule, not a validated business policy.

## Monitoring and Drift

Successful local API predictions are logged to:

```text
logs/predictions.jsonl
```

Sample prediction traffic is synthetic. Simulated drift detection compares reference prediction logs with a deterministic shifted current batch. Drift thresholds are simple demonstration thresholds.

The Streamlit dashboard visualises local prediction logs and simulated drift results. This is not live production monitoring.

## Ethical and Responsible Use Considerations

False positives may trigger unnecessary retention action. False negatives may miss customers who are likely to churn. Model outputs should support human review rather than automated customer treatment.

Customer treatment should avoid unfair or discriminatory handling. The public dataset may not represent real customer populations, and subgroup fairness is not fully validated in this project.

Privacy considerations matter if this project is adapted to real data. Local prediction logs intentionally avoid identifiers such as `customerID`, but logs could become privacy-sensitive if expanded to real customer records.

## Limitations

- Public static dataset.
- No real production traffic.
- No ground-truth labels for simulated prediction logs.
- Simulated drift only.
- No cloud deployment.
- No live monitoring or alerting.
- No validated economic impact.
- No model registry or production governance workflow.

## Recommended Next Steps

- Add subgroup performance analysis.
- Add threshold analysis.
- Add API latency benchmark.
- Add stronger drift metrics if needed.
- Add model comparison with tree-based baselines.
- Improve dashboard screenshots and project evidence.
- Finalise CV, LinkedIn and interview STAR story wording.
