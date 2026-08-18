# Model and Data

## Problem Framing

Customer churn prediction is a binary classification problem for identifying customers who may discontinue a subscription service. In a realistic workflow, a prediction should support human review rather than automatically determine customer treatment.

This project uses the problem to demonstrate the engineering lifecycle around a tabular model: reproducible preprocessing, held-out evaluation, artifact persistence, API serving, testing, deployment and monitoring evidence.

## Dataset

The project uses the public Telco Customer Churn dataset with `Churn` as the target. The raw CSV is intentionally excluded from Git and is expected at:

```text
data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv
```

| Property | Value |
| --- | ---: |
| Records | 7,043 |
| Raw columns | 21 |
| Model features | 19 |
| Non-churn records | 5,174 |
| Churn records | 1,869 |
| Training records | 5,634 |
| Held-out test records | 1,409 |

The data is public, static and relatively small. It may not represent current or organisation-specific customer populations.

## Cleaning and Preprocessing

[`src/data/load_data.py`](../src/data/load_data.py) applies the dataset-specific cleaning rules:

- drops `customerID` before modelling;
- converts `TotalCharges` to numeric, coercing blank values to missing values;
- maps `Churn` from `No`/`Yes` to `0`/`1`; and
- separates the target from the 19 model features.

The raw dataset contains 11 `TotalCharges` values that become missing after numeric conversion. Missing-value handling remains inside the fitted preprocessing pipeline.

[`src/features/preprocessing.py`](../src/features/preprocessing.py) builds a `ColumnTransformer` with:

- median imputation and standard scaling for numerical features;
- most-frequent imputation and one-hot encoding for categorical features; and
- `handle_unknown="ignore"` for unseen categorical levels.

The fitted transformer and classifier are persisted together so inference uses the same preprocessing learned during training.

## Baseline and Model Choice

The notebook baseline in [`notebooks/01_baseline_experiment.ipynb`](../notebooks/01_baseline_experiment.ipynb) established the initial data and modelling workflow. The reusable implementation under `src/` then preserved the same fixed split and modelling assumptions.

Two models are evaluated:

- `DummyClassifier(strategy="prior")` as a non-informative sanity-check baseline;
- `LogisticRegression(max_iter=1000, random_state=42)` as the fitted churn model.

Logistic regression was selected as a transparent and practical baseline for tabular binary classification. Complex tuning and tree-based models were deliberately kept outside the initial scope so the project could focus on the ML engineering lifecycle.

## Held-Out Evaluation

| Model | ROC-AUC | Accuracy | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| DummyClassifier | 0.5000 | 0.7346 | 0.0000 | 0.0000 | 0.0000 |
| LogisticRegression | 0.8419 | 0.8055 | 0.6572 | 0.5588 | 0.6040 |

The `LogisticRegression` pipeline substantially improves ROC-AUC and F1 over the dummy baseline. Accuracy alone is not sufficient because the target is imbalanced.

Recall and precision remain moderate. False negatives may miss customers likely to churn, while false positives may trigger unnecessary retention review. Threshold analysis would be required before adapting the output to a real business process.

## Prediction Interface

The API accepts the 19 model features and returns:

- `churn_probability`;
- `churn_prediction`; and
- a demonstration `risk_label`.

Risk labels use fixed local demonstration thresholds: `high` at probability 0.65 or above, `medium` at 0.35 or above, and `low` otherwise. These thresholds are not a validated retention policy.

## Responsible Use

- Use predictions as decision support with human review.
- Do not use this model for automatic customer treatment or high-stakes decisions.
- Do not infer real retention uplift or business impact from held-out metrics.
- Validate privacy, fairness, calibration and subgroup performance before any use with real customer data.
- Treat the Azure deployment and synthetic benchmark as portfolio evidence, not production suitability or an SLA.

## Evidence

- [Baseline experiment summary](../reports/baseline_summary.md)
- [Evaluation summary](../reports/evaluation_summary.md)
- [Model card](../reports/model_card.md)
- [Risk register](../reports/risk_register.md)
- [Training metrics](../reports/training_metrics.json)
