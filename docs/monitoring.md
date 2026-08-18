# Monitoring and Observability

This project deliberately separates local ML monitoring evidence from Azure runtime observability. Neither is presented as production monitoring.

## Monitoring Boundaries

| Area | Scope | Evidence |
| --- | --- | --- |
| Local ML monitoring | Synthetic API traffic, JSONL prediction logs, simulated drift and Streamlit visualisation | Local files and committed drift reports |
| Azure runtime observability | Container lifecycle, application startup and HTTP request evidence | Azure Container Apps logs and Log Analytics queries |

The local Streamlit dashboard and simulated drift workflow are not deployed to Azure. Azure Log Analytics does not provide production model-performance or production drift monitoring in this project.

## Prediction Logging

Each successful local `POST /predict` request appends one JSON object to:

```text
logs/predictions.jsonl
```

Events contain:

- UTC timestamp and request ID;
- model artifact path;
- churn probability, predicted class and risk label; and
- selected monitoring features: `tenure`, `MonthlyCharges`, `TotalCharges`, `Contract`, `InternetService` and `PaymentMethod`.

The logger excludes `customerID`. The generated JSONL file is excluded from Git and should not be treated as an approved logging design for real customer data.

## Generate Synthetic Traffic

Train or retrieve the model artifact and start the API:

```bash
python -m uvicorn app.main:app --reload
```

In a second terminal, send synthetic Telco-like requests through the real API path:

```bash
python -m scripts.generate_sample_prediction_traffic --n 30
```

The script appends successful events to `logs/predictions.jsonl` and writes `reports/sample_prediction_traffic_summary.md`. This is synthetic local traffic, not production traffic.

## Simulated Drift Detection

After generating prediction logs:

```bash
python -m scripts.run_simulated_drift_detection
```

Outputs:

```text
reports/drift_detection_results.json
reports/drift_detection_summary.md
```

The workflow creates a deterministic shifted batch from the local reference prediction logs. It checks:

- mean shifts for `tenure`, `MonthlyCharges`, `TotalCharges` and `churn_probability`; and
- categorical proportion shifts for `Contract`, `InternetService`, `PaymentMethod` and `risk_label`.

The current demonstration thresholds are a 20% relative mean shift for numerical features and a 25 percentage-point maximum distribution shift for categorical features. These transparent thresholds are portfolio controls, not calibrated production alert thresholds.

Because the current batch is simulated and no ground-truth outcomes are available, the result does not establish real model degradation or production drift.

## Streamlit Dashboard

With prediction and drift evidence available, start the local dashboard:

```bash
python -m streamlit run dashboard/streamlit_app.py
```

The dashboard reads `logs/predictions.jsonl` and `reports/drift_detection_results.json` and displays:

- prediction event count and churn probability summaries;
- risk-label counts and distribution;
- numerical and categorical monitoring feature summaries;
- numerical and categorical drift tables; and
- the simulation note and overall drift flag.

The dashboard is a local portfolio interface. It is not hosted in Azure and does not provide live production alerting.

## Azure Runtime Observability

The Azure-hosted FastAPI service produced validated runtime evidence through Azure Container Apps and Azure Log Analytics:

- system logs confirmed image pull, container creation and container startup;
- console logs confirmed Uvicorn startup and successful `/health`, synthetic `/predict` and `/docs` requests; and
- persistent queries were validated against `ContainerAppConsoleLogs_CL` and `ContainerAppSystemLogs_CL`.

A startup probe warning was followed by successful startup and endpoint responses and was not treated as an outage. The Consumption app was observed scaling down after inactivity, but that observation does not establish an availability guarantee, cost guarantee or SLA.

Detailed cloud validation and guardrails remain in the [Azure deployment plan](azure_deployment_plan.md).

## Limitations

- Prediction traffic and drift are synthetic.
- Drift checks use demonstration thresholds and no ground-truth labels.
- Local JSONL files are not a production event store.
- The Streamlit dashboard is local and has no automated alerts.
- Azure logs demonstrate runtime behaviour, not model quality, business outcomes or production drift.
- Privacy and retention controls would require redesign before logging real customer data.

## Evidence

- [Sample prediction traffic summary](../reports/sample_prediction_traffic_summary.md)
- [Simulated drift summary](../reports/drift_detection_summary.md)
- [Simulated drift JSON](../reports/drift_detection_results.json)
- [Model card](../reports/model_card.md)
- [Risk register](../reports/risk_register.md)
