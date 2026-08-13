# Azure-Hosted API Latency Benchmark

This is a client-observed synthetic benchmark of the Azure-hosted portfolio endpoint, not a production performance or SLA test. It is not a load test, stress test or pure model inference benchmark.

- Benchmark type: Azure-hosted synthetic API latency
- Benchmark origin: local workstation
- Transport: HTTPS
- Request mode: sequential
- Timestamp: `2026-08-12T23:58:57.648165+00:00`
- Base URL: `https://ca-mlops-churn-api.delightfulrock-f1f751cc.swedencentral.azurecontainerapps.io`
- Prediction URL: `https://ca-mlops-churn-api.delightfulrock-f1f751cc.swedencentral.azurecontainerapps.io/predict`
- Readiness attempts: 2
- Unmeasured warm-up requests: 5
- Requests attempted: 100
- Requests succeeded: 100
- Requests failed: 0
- Success rate: 100.00%

Latency measurement begins after readiness validation and unmeasured warm-up requests. This does not completely characterize or eliminate all cold-start effects.

Latency scope: client-observed end-to-end successful POST /predict requests only.
The duration may include client-side handling, public network latency, HTTPS transport, Azure Container Apps ingress, FastAPI handling, preprocessing, model inference and response transmission.

## Latency Metrics

| Metric | Value |
| --- | ---: |
| Average | 56.947 ms |
| p50 | 55.676 ms |
| p95 | 61.961 ms |
| Minimum | 53.788 ms |
| Maximum | 98.342 ms |
