# MLflow Run Summary

- Experiment name: `telco-churn-baseline`
- Run ID: `28af94afc0a14fcea12e7388336c8922`
- Logged model type: `LogisticRegression`
- Baseline model: `DummyClassifier`
- Model artifact path: `artifacts/model_pipeline.joblib`
- Training metrics report: `reports/training_metrics.json`

## LogisticRegression Metrics

- ROC-AUC: 0.8419
- Accuracy: 0.8055
- Precision: 0.6572
- Recall: 0.5588
- F1: 0.604

## DummyClassifier Metrics

- ROC-AUC: 0.5
- Accuracy: 0.7346
- Precision: 0.0
- Recall: 0.0
- F1: 0.0

## Local MLflow UI

Start the local UI from the project root:

```bash
mlflow ui
```

Open:

```text
http://127.0.0.1:5000
```
