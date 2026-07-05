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
