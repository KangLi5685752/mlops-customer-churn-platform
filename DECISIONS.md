# Decision Log

## 2026-06-26: Use Telco Customer Churn as the project dataset

Decision: Use the Telco Customer Churn dataset as the project dataset.

Reason: The dataset has clear business framing, supports customer-level prediction, uses a tabular ML workflow and is suitable for API serving and simulated drift monitoring.

## 2026-06-26: Frame the project as a customer churn prediction MLOps prototype

Decision: Frame the project as a customer churn prediction MLOps prototype.

Reason: This is closer to real business ML workflows than a generic classification demo and gives the project a clear lifecycle from experimentation to serving and monitoring.

## 2026-06-26: Use a notebook/script baseline first

Decision: Start with a notebook/script baseline before adding MLOps components.

Reason: A notebook/script workflow is a reasonable experimentation-stage baseline, not a deliberately weak baseline. It gives the project a realistic starting point for later refactoring.

## 2026-06-26: Use scikit-learn for the MVP

Decision: Use scikit-learn for the MVP modelling workflow.

Reason: scikit-learn is fast to implement, reliable for tabular data and easier to integrate with FastAPI, pytest and MLflow.

## 2026-06-26: Keep the MVP local and production-style rather than production-deployed

Decision: Keep the MVP local while using production-style engineering practices.

Reason: This avoids overclaiming. Metrics will come from held-out test data, local benchmarking and simulated traffic rather than a real production deployment.

## 2026-06-26: Exclude Kubernetes, cloud deployment, complex databases and streaming systems from MVP

Decision: Exclude Kubernetes, cloud deployment, complex database architecture and real-time streaming systems from the MVP scope.

Reason: These are too much scope for the current portfolio sprint and are not necessary to demonstrate the core MLOps lifecycle.

## 2026-06-26: Treat churn prediction outputs as decision support

Decision: Treat churn prediction outputs as decision support, not automated customer treatment.

Reason: False positives, false negatives and unfair customer handling are potential risks. Human review should remain part of any realistic customer treatment workflow.

## 2026-06-27: Keep the original Telco dataset filename

Decision: Keep the original dataset filename `WA_Fn-UseC_-Telco-Customer-Churn.csv`.

Reason: Keeping the original filename improves reproducibility, avoids hidden data-renaming assumptions and makes user setup easier to verify.

## 2026-06-27: Drop customerID before modelling

Decision: Drop `customerID` as an identifier before model training.

Reason: The identifier is not a meaningful predictive feature and could encourage leakage-like memorisation patterns that do not generalise.

## 2026-06-27: Convert TotalCharges to numeric and impute missing values in preprocessing

Decision: Convert `TotalCharges` with `pandas.to_numeric(..., errors="coerce")` and handle missing values through median imputation inside the preprocessing pipeline.

Reason: The raw column is stored as text and contains blank values. Handling missing values in the pipeline keeps the baseline closer to a reproducible training workflow.

## 2026-06-27: Use DummyClassifier as a sanity-check baseline

Decision: Include `DummyClassifier` with a simple prior-based strategy.

Reason: It provides a trivial reference point and confirms that the main baseline is being compared against a non-informative model.

## 2026-06-27: Use LogisticRegression as the first reasonable baseline model

Decision: Use `LogisticRegression` as the first real baseline model.

Reason: Logistic regression is simple, transparent, appropriate for tabular binary classification and easy to combine with scikit-learn preprocessing pipelines.

## 2026-06-27: Keep model comparison simple at the baseline stage

Decision: Avoid complex model tuning, XGBoost, LightGBM and deep learning during Stage 2.

Reason: The project scope is to establish a credible experimentation baseline before demonstrating refactoring, reproducibility, API serving, tests and monitoring.

## 2026-06-29: Save the full model pipeline artifact

Decision: Save the full scikit-learn preprocessing and LogisticRegression pipeline as `artifacts/model_pipeline.joblib`.

Reason: The future API should load the same preprocessing and model steps used during training, rather than relying on a bare model with duplicated preprocessing logic.

## 2026-06-29: Keep generated model artifacts out of Git

Decision: Keep generated model artifacts such as `artifacts/model_pipeline.joblib` out of Git.

Reason: Model artifacts are local generated outputs and can be recreated from the training command. Keeping them out of Git avoids repository bloat and stale binary files.

## 2026-06-29: Require evaluate.py to load the saved artifact

Decision: Make `src/models/evaluate.py` load `artifacts/model_pipeline.joblib` instead of silently retraining the main LogisticRegression model.

Reason: Evaluation should validate the artifact that future serving code will use. If the artifact is missing, the user should explicitly run `python -m src.models.train`.

## 2026-07-03: Keep early tests independent of the raw dataset

Decision: Use small synthetic pandas DataFrames for early pytest validation instead of depending on the raw Telco CSV file.

Reason: The raw dataset is intentionally excluded from Git. Synthetic-data tests can run in future CI without committing data while still validating cleaning, preprocessing and baseline pipeline behaviour.

## 2026-07-04: Keep API serving separate from training

Decision: The FastAPI serving layer loads `artifacts/model_pipeline.joblib` and does not train or retrain models.

Reason: Serving should use the same saved preprocessing and model pipeline generated by the training workflow. This keeps training and inference responsibilities separate.

## 2026-07-04: Use simple local risk-label thresholds

Decision: Map churn probability to local prototype risk labels using `high` for probability >= 0.65, `medium` for probability >= 0.35 and `low` otherwise.

Reason: A simple threshold rule is readable for the MVP API. It is a local demonstration rule, not a validated business policy.

## 2026-07-04: Mock model loading in API endpoint tests

Decision: API endpoint tests mock `load_model_pipeline` instead of loading `artifacts/model_pipeline.joblib`.

Reason: The model artifact is intentionally excluded from Git. Mocking model loading keeps endpoint tests suitable for future CI without committing generated artifacts or raw data.

## 2026-07-04: Copy local model artifact into the Docker image

Decision: For the local Docker MVP, copy the locally generated `artifacts/model_pipeline.joblib` into the image after running the training script, while keeping the artifact out of Git.

Reason: The API container needs the saved preprocessing and model pipeline at runtime, but generated binary artifacts should remain reproducible local outputs rather than committed source files.

## 2026-07-04: Keep model training separate from Docker build

Decision: The Dockerfile does not train the model. Users must run `python -m src.models.train` before building the image.

Reason: Keeping training outside the image build makes the container serve an explicit saved artifact and avoids hidden training side effects during packaging.

## 2026-07-05: Keep the first CI workflow focused on pytest

Decision: The first GitHub Actions workflow runs dependency installation and `python -m pytest`, without running training or Docker build validation.

Reason: The test suite is intentionally independent of the raw Telco CSV and generated model artifacts. Docker build validation remains a separate concern from the initial CI check.

## 2026-07-06: Use local file-based MLflow tracking for the MVP

Decision: Log training parameters, metrics and generated artifacts to local file-based MLflow runs under `mlruns/`, while keeping `mlruns/` out of Git.

Reason: Local MLflow tracking gives useful experiment evidence without adding a tracking server, model registry, cloud service or deployment workflow. The generated run metadata can grow quickly and is reproducible from local training runs, so it should remain uncommitted.

## 2026-07-07: Use JSONL for local prediction logs

Decision: Append successful API prediction events to `logs/predictions.jsonl` using one JSON object per line, while logging only selected monitoring features rather than the full raw request payload.

Reason: JSONL is simple, append-friendly and easy to inspect locally. Logging a focused feature subset keeps the MVP more privacy-conscious while still creating useful input for later simulated drift detection. Prediction logs are generated runtime outputs and should remain out of Git.

## 2026-07-07: Generate sample traffic through the API

Decision: Generate synthetic local sample prediction traffic by sending valid Telco payloads to the running FastAPI `/predict` endpoint instead of writing prediction logs directly.

Reason: Sending traffic through the API ensures sample prediction logs are produced by the same path used during inference. The generated traffic is synthetic local traffic for monitoring demonstrations, not production traffic.

## 2026-07-07: Use transparent simulated drift checks before dashboarding

Decision: Add simple numerical mean-shift checks and categorical proportion-shift checks using a deterministic simulated current batch before adding any dashboard.

Reason: There is no real production traffic in this local portfolio project. Simulated drift makes the monitoring workflow demonstrable while keeping thresholds transparent and clearly non-production.

## 2026-07-08: Use Streamlit for the local monitoring dashboard

Decision: Use a file-based Streamlit dashboard that reads local prediction logs and simulated drift reports instead of adding a database or production monitoring stack.

Reason: Streamlit is lightweight and suitable for portfolio monitoring visualisation. Reading local files keeps the dashboard aligned with the MVP scope and makes it clear that this is local prototype evidence, not production observability.

## 2026-08-12: Use Azure as the first cloud platform

Decision: Use the Azure for Students subscription as the first cloud platform for Stage 11, with Azure Container Registry and Azure Container Apps as the cloud MVP direction.

Reason: The existing API is already containerised, and this direction provides a focused path to demonstrate a cost-controlled cloud deployment without adding Kubernetes administration or unrelated infrastructure.

## 2026-08-12: Deploy Stage 11 resources in UK South

Decision: Use UK South for Stage 11 resources where the selected Azure service supports it.

Reason: A single selected region keeps resource management, cost review, evidence collection and teardown simpler for the portfolio MVP.

## 2026-08-12: Use GitHub OIDC with least-privilege deployment access

Decision: Authenticate future GitHub Actions deployment through OIDC federation using `id-github-mlops-churn`, with permissions scoped as narrowly as practical to `rg-mlops-churn-portfolio`.

Reason: OIDC avoids storing long-lived Azure client secrets in GitHub. Pull request workflows must not deploy, and normal CI/CD deployment does not require subscription-wide Owner access.

## 2026-08-12: Use a cost-controlled, teardown-first cloud MVP

Decision: Treat the Azure deployment as temporary, cost-controlled portfolio evidence and plan teardown before provisioning runtime resources.

Reason: The Azure for Students credit is limited. The £10 monthly budget and actual-cost alerts provide guardrails, while deleting project resources after evidence collection limits unnecessary ongoing spend. This remains a cloud deployment MVP, not an enterprise production deployment.

## 2026-08-12: Retrieve a pinned deployment artifact and verify it before use

Decision: Keep `model_pipeline.joblib` outside Git and define its provenance in `deployment/model_artifact.json`. Future clean deployment builds must retrieve the pinned GitHub Release asset and verify its authoritative SHA-256 checksum before installing or loading it. Deployment builds must never load an unverified joblib/pickle artifact.

Reason: Separating the validated deployment artifact from source code preserves the existing generated-artifact policy and avoids coupling deployment to retraining or access to the Git-ignored raw dataset. Pinning scikit-learn and joblib to the validated runtime versions reduces serialization compatibility risk. The `model-v1.0.0` release has now been published with the `model_pipeline.joblib` asset, and GitHub reports the same SHA-256 as the manifest. Real clean-runner/network retrieval remains to be validated, and no Azure runtime or workload resources were provisioned by the release step.

## 2026-08-13: Use Sweden Central for Azure workload resources

Decision: Deploy the Stage 11 Azure Container Registry and Container Apps workload resources in Sweden Central instead of the originally intended UK South region.

Reason: The Azure for Students subscription region policy prevented the intended UK South workload deployment. Sweden Central supported the required services and was used for the manually validated cloud-hosted portfolio deployment. This is a subscription-policy adjustment, not an expansion of infrastructure scope.
