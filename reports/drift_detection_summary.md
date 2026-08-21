# Simulated Drift Detection Summary

- Timestamp: `2026-08-19T14:07:26.942839+00:00`
- Reference records: 123
- Simulated current records: 123
- Overall result: Drift detected

The current batch is simulated by applying controlled feature shifts to local prediction logs.

## Numerical Drift

| Feature | Reference Mean | Current Mean | Difference | Percent Difference | Drift |
| --- | ---: | ---: | ---: | ---: | --- |
| tenure | 26.1463 | 20.1626 | -5.9837 | -22.89% | True |
| MonthlyCharges | 59.4602 | 68.186 | 8.7259 | 14.68% | False |
| TotalCharges | 1194.3512 | 1029.7267 | -164.6245 | -13.78% | False |
| churn_probability | 0.3043 | 0.4543 | 0.15 | 49.29% | True |

## Categorical Drift

| Feature | Max Proportion Difference | Drift |
| --- | ---: | --- |
| Contract | 0.3252 | True |
| InternetService | 0.4634 | True |
| PaymentMethod | 0.0 | False |
| risk_label | 0.3333 | True |

## Limitations

- Based on synthetic local prediction logs.
- Not real production monitoring.
- No ground-truth `Churn` labels are used.
- Thresholds are simple demonstration thresholds, not validated alert thresholds.
