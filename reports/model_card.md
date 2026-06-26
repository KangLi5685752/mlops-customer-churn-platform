# Model Card

This is a template for the future churn prediction model card. No model has been trained at this setup stage.

## Model Details

To be completed after model training.

## Intended Use

The model is intended to estimate customer churn risk for a portfolio-grade MLOps prototype using the Telco Customer Churn dataset. Predictions should support human review and experimentation rather than automated customer treatment.

## Out-of-Scope Use

- Real customer treatment decisions without human review.
- Use on real customer data without privacy, security and fairness review.
- Claims of production readiness or real business impact.
- Use outside the dataset and feature assumptions validated during evaluation.

## Dataset

The planned dataset is the Telco Customer Churn dataset. The target variable is `Churn`. The repository will not include the dataset file.

## Features

To be completed after the feature preprocessing pipeline is implemented. Expected feature groups include customer demographics, service subscription information, account information and billing-related features.

## Training Procedure

To be completed after the baseline training workflow is implemented.

## Evaluation Metrics

Planned model evaluation metrics include:

- ROC-AUC
- F1
- precision
- recall
- confusion matrix

No evaluation results are available at this setup stage.

## Ethical Considerations

Churn prediction can affect how customers are prioritised for retention actions. Predictions should be reviewed by humans, and any real-world use would require consideration of fairness, privacy and customer impact.

## Limitations

- The dataset is small and public.
- Simulated traffic is not the same as real production traffic.
- Model behaviour may change under feature drift.
- False positives and false negatives have different business implications.

## Monitoring Plan

The planned monitoring approach is simulated drift detection using generated or replayed customer profiles. Features such as `tenure`, `MonthlyCharges` and `Contract` may be used to demonstrate feature drift.

## Human Review and Escalation

Predictions should support human review rather than automatically determine customer treatment. High-risk predictions should be interpreted alongside business context and customer history.

## Future Improvements

To be completed as the project progresses.
