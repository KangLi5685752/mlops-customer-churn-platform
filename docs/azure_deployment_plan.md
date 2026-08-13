# Azure Deployment Plan

## Status

This document began as the Stage 11.0 cloud deployment plan and guardrails. It now also records the validated Stage 11.2 through 11.6 cloud-hosted portfolio deployment and benchmark evidence.

The Azure resource group `rg-mlops-churn-portfolio` was created with UK South as its resource-group location. The Azure workload resources were deployed in Sweden Central because the Azure for Students subscription region policy prevented the originally intended UK South deployment. The project remains a cost-controlled portfolio cloud deployment MVP, not a production deployment.

## Stage 11 Scope

Stage 11 is intended to extend the completed local MLOps workflow with a small Azure deployment, GitHub Actions deployment automation and basic cloud observability evidence.

The intended cloud MVP will:

- publish the existing API container image to Azure Container Registry;
- run the existing FastAPI service in Azure Container Apps;
- use Log Analytics for the minimum practical platform logs and observability evidence;
- use GitHub Actions with OpenID Connect (OIDC) for deployment authentication;
- validate the deployed health and prediction endpoints with synthetic requests; and
- collect portfolio evidence before applying the teardown policy when a live endpoint is no longer required.

This scope does not imply enterprise production readiness, production traffic, a production SLA, large-scale cloud infrastructure or real customer impact.

## Azure Platform Choice

Azure is the first cloud platform for this portfolio project. The selected cloud MVP direction is Azure Container Registry (ACR) plus Azure Container Apps because it supports a container-based API deployment without introducing Kubernetes cluster administration.

The subscription is `Azure for Students`. At the start of Stage 11, the available credit was $100 equivalent / £75.25, with 0% used and an expiration date of 2027-08-11.

## Region

UK South was the intended workload region. The Azure for Students subscription region policy required the Stage 11.2 through 11.4 workload resources to use Sweden Central instead. ACR and Container Apps were therefore manually validated in Sweden Central; this region change is recorded rather than presented as the original plan.

## Resource Naming

| Resource | Intended name | Notes |
| --- | --- | --- |
| Resource Group | `rg-mlops-churn-portfolio` | Created with UK South as its resource-group location. |
| Azure Container Registry | `acrmlopschurnkl5685752` | Created in Sweden Central with Basic SKU. |
| Container Apps Environment | `cae-mlops-churn` | Created in Sweden Central. |
| Container App | `ca-mlops-churn-api` | Running in Sweden Central on the Consumption workload profile. |
| Log Analytics Workspace | `log-mlops-churn` | Used for validated persistent Container Apps log queries. |
| GitHub deployment identity | `id-github-mlops-churn` | OIDC federation and manual deployment validated from this repository's `main` branch. |

The workload resource names were validated during manual deployment. The GitHub deployment identity is configured for OIDC federated authentication without long-lived Azure client secrets.

## Completed Manual Validation

### Stage 11.2: Azure Container Registry

- Manually pushed `mlops-churn-api:fcd471855395` to `acrmlopschurnkl5685752`.
- Verified repository, tag and registry manifest digest through Azure CLI queries.
- Validated digest: `sha256:db8466a6f629f6fbb3cd270b2b917fd00b7c77d18a8df56d455c5ff634100dde`.

### Stage 11.3: Azure Container Apps

- Deployed `ca-mlops-churn-api` to `cae-mlops-churn` with the Consumption workload profile and `0.5 vCPU / 1 GiB`.
- Configured external HTTPS ingress to container port 8000 and managed identity for registry authentication.
- Confirmed Running state and validated `/health`, `/predict` with a synthetic request, and `/docs`.
- Confirmed the cloud prediction matched the validated local Docker result for the same synthetic payload.

### Stage 11.4: Observability

- Confirmed live system logs for image pull, container creation and startup.
- Confirmed live console logs for Uvicorn startup and HTTP 200 responses from `/health`, `/predict` and `/docs`.
- Validated persistent queries against `ContainerAppConsoleLogs_CL` and `ContainerAppSystemLogs_CL`.
- Observed a startup probe warning followed by successful startup and requests; this was not an outage.
- Observed the Consumption replica scale down after inactivity without inferring a production SLA, availability guarantee or specific cost saving.

### Stage 11.5: GitHub Actions OIDC and Manual Deployment

- Stage 11.5A created user-assigned managed identity `id-github-mlops-churn`.
- Stage 11.5B configured GitHub-to-Azure federation for `KangLi5685752/mlops-customer-churn-platform` on `main`.
- Stage 11.5C configured resource-scoped RBAC: `AcrPush` plus `Container Registry Configuration Reader and Data Access Configuration Reader` at the ACR resource, and `Container Apps Contributor` at `rg-mlops-churn-portfolio`.
- The registry configuration reader role was added narrowly after validation showed that `AcrPush` alone did not allow `az acr login --expose-token` to resolve the non-default login server `acrmlopschurnkl5685752-ddhkccgxcecpfjb6.azurecr.io`.
- Stage 11.5D validated OIDC token issuance, `main`-branch subject binding, Azure CLI federated login and read access to the subscription and existing Container App.
- Stage 11.5E manually ran `.github/workflows/azure-deploy.yml` from `main` and passed all 34 tests.
- The workflow retrieved the pinned GitHub Release artifact, verified its SHA-256 and confirmed `artifacts/model_pipeline.joblib` existed before building; it did not train the model or store the artifact in Git.
- It built and pushed immutable image tag `b613f29250c3` from source commit `b613f29250c3b4c14b54a4c5a7a7a39579effaca`, with digest `sha256:10d9aab1516f80e0c54edd05cb6410efb7d8a7a341c85ee7270b97f3aaa1805a`.
- It recorded previous tag `fcd471855395`, updated only the Container App image and independently verified that Azure reported the new immutable image reference.
- The bounded HTTPS `/health` smoke test passed on attempt 2 with `status: ok` and `model_artifact_exists: true`; the first timeout accommodated revision startup and was not an outage.
- Stage 11.5F enabled and validated automatic deployment for deployment-relevant pushes to `main`, while preserving manual dispatch.
- Stage 11.5G added PR Docker build validation after pytest and verified artifact retrieval; PR workflows do not authenticate to Azure, push images or deploy.
- Stage 11.5 is complete.

### Stage 11.6: Azure-Hosted Latency Evidence

- Added a separate Azure-hosted benchmark harness and separate report paths so local benchmark evidence remains unchanged.
- Executed the benchmark from a local workstation over public HTTPS using sequential synthetic `/predict` requests.
- Readiness passed on bounded attempt 2, followed by 5 successful unmeasured warm-up requests; neither readiness nor warm-up was included in prediction latency statistics.
- Measured 100 requests with 100 successes and 0 failures.
- Recorded `56.947 ms` average, `55.676 ms` p50, `61.961 ms` p95, `53.788 ms` minimum and `98.342 ms` maximum client-observed end-to-end latency.
- The result may include workstation handling, public networking, HTTPS transport, Container Apps ingress, application handling, preprocessing, model inference and response transmission.
- This is not pure model inference latency, production traffic, a load or stress test, an SLA measurement or a production performance benchmark.
- Stage 11.6 is complete.

## Cost Guardrails

- Use the existing billing budget `budget-mlops-portfolio`.
- Keep the monthly budget at £10.
- Keep actual-cost alerts at 50%, 80% and 100%.
- Deploy only resources required for the cloud MVP and prefer low-cost or consumption-based configuration where practical.
- Review Azure Cost Management and remaining student credit during deployment validation and again after teardown.
- Remove cloud runtime resources after the required evidence is collected when a live endpoint is no longer needed.
- Keep the £10 billing budget as an account-level guardrail unless it is explicitly removed later.

A budget and alerts help detect spend but do not automatically stop or delete Azure resources.

## Deployment Identity and Resource-Scoped RBAC

GitHub Actions deployment uses OIDC federation rather than a long-lived Azure client secret or password. The federated subject is restricted to this repository's `main` branch. Pull request workflows must never deploy Azure resources.

The deployment identity uses resource-scoped RBAC with narrowly scoped registry and Container Apps permissions. It has `AcrPush` and `Container Registry Configuration Reader and Data Access Configuration Reader` at the ACR resource, plus `Container Apps Contributor` at the project resource group. It does not use subscription-wide Owner access for deployment. Role assignments should be reviewed and removed during teardown when no longer required.

## Secret-Handling Policy

- Do not commit Azure credentials, access keys, passwords, tokens or generated credential files to Git.
- Do not create a long-lived Azure client secret for GitHub Actions.
- Store only non-secret identifiers required by OIDC configuration in GitHub repository or environment configuration.
- Treat subscription, tenant and client identifiers as configuration metadata and avoid exposing them unnecessarily in reports or screenshots.
- Use GitHub environment protections for deployment where practical.
- Redact sensitive values from terminal output, screenshots and portfolio evidence.
- Prefer Azure identity and role-based access control over registry admin credentials or embedded passwords.

## Cloud Build Artifact Guardrail

The validated `model_pipeline.joblib` remains outside Git. Its provenance, runtime compatibility and authoritative SHA-256 checksum are recorded in `deployment/model_artifact.json`. The `model-v1.0.0` GitHub Release has been published with the `model_pipeline.joblib` asset, and GitHub reports the same SHA-256 as the manifest. A real GitHub-hosted deployment run successfully retrieved and verified the artifact before Docker build.

Before every Docker build on a clean runner, the pinned release asset must be downloaded to a temporary file and verified against the manifest checksum. It may only be installed at `artifacts/model_pipeline.joblib` after verification succeeds. Deployment builds must never load an unverified joblib/pickle artifact.

## Explicitly Out of Scope

The Stage 11 cloud MVP does not include:

- changes to the Docker application or model workflow;
- Terraform or Bicep;
- Kubernetes or AKS;
- Databricks or Spark;
- databases, authentication or unrelated infrastructure;
- enterprise production deployment claims, production traffic, production SLAs or real customer impact.

## Intended Stage 11 Sequence

1. Completed: Stage 11.0 recorded Azure scope, names, security decisions, cost controls and teardown requirements.
2. Completed: defined the versioned deployment artifact manifest and checksum-gated retrieval process.
3. Completed manually: built and pushed the validated image to ACR and verified its tag and digest in Stage 11.2.
4. Completed manually: deployed the Container App and validated `/health`, `/docs` and `/predict` with a synthetic request in Stage 11.3.
5. Completed manually: validated live and persistent Container Apps logs through Log Analytics in Stage 11.4.
6. Completed: configured GitHub OIDC federation, resource-scoped RBAC and a real read-only OIDC smoke test in Stages 11.5A through 11.5D.
7. Completed manually: validated the end-to-end deployment workflow, immutable image update, deployed-image query and bounded `/health` check in Stage 11.5E.
8. Completed: enabled and validated automatic deployment from `main` for deployment-relevant changes, with cloud-write-free PR Docker validation.
9. Completed: recorded separate Azure-hosted client-observed latency evidence in Stage 11.6.
10. Next: package portfolio, CV, LinkedIn and interview evidence in Stage 11.7.
11. Later: follow `docs/azure_teardown_checklist.md` when a live endpoint is no longer required.
