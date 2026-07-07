# Simulated Drift Detection Summary

- Timestamp: `2026-07-07T15:11:54.866905+00:00`
- Reference records: 92
- Simulated current records: 92
- Overall result: Drift detected

The current batch is simulated by applying controlled feature shifts to local prediction logs.

## Numerical Drift

| Feature | Reference Mean | Current Mean | Difference | Percent Difference | Drift |
| --- | ---: | ---: | ---: | ---: | --- |
| tenure | 26.1848 | 19.5217 | -6.663 | -25.45% | True |
| MonthlyCharges | 59.6223 | 68.8889 | 9.2666 | 15.54% | False |
| TotalCharges | 1197.6033 | 1020.5372 | -177.0661 | -14.79% | False |
| churn_probability | 0.3035 | 0.4535 | 0.15 | 49.43% | True |

## Categorical Drift

| Feature | Max Proportion Difference | Drift |
| --- | ---: | --- |
| Contract | 0.3261 | True |
| InternetService | 0.4674 | True |
| PaymentMethod | 0.0 | False |
| risk_label | 0.337 | True |

## Limitations

- Based on synthetic local prediction logs.
- Not real production monitoring.
- No ground-truth `Churn` labels are used.
- Thresholds are simple demonstration thresholds, not validated alert thresholds.
