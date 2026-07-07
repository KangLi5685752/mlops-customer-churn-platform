# Simulated Drift Detection Summary

- Timestamp: `2026-07-07T16:11:39.426978+00:00`
- Reference records: 122
- Simulated current records: 122
- Overall result: Drift detected

The current batch is simulated by applying controlled feature shifts to local prediction logs.

## Numerical Drift

| Feature | Reference Mean | Current Mean | Difference | Percent Difference | Drift |
| --- | ---: | ---: | ---: | ---: | --- |
| tenure | 26.2623 | 20.082 | -6.1803 | -23.53% | True |
| MonthlyCharges | 59.7029 | 68.1198 | 8.4169 | 14.10% | False |
| TotalCharges | 1201.2049 | 1038.7666 | -162.4383 | -13.52% | False |
| churn_probability | 0.3031 | 0.4531 | 0.15 | 49.48% | True |

## Categorical Drift

| Feature | Max Proportion Difference | Drift |
| --- | ---: | --- |
| Contract | 0.3279 | True |
| InternetService | 0.459 | True |
| PaymentMethod | 0.0 | False |
| risk_label | 0.3361 | True |

## Limitations

- Based on synthetic local prediction logs.
- Not real production monitoring.
- No ground-truth `Churn` labels are used.
- Thresholds are simple demonstration thresholds, not validated alert thresholds.
