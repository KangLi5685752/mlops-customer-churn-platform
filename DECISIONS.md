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
