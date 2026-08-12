# Azure Deployment Plan

## Status

This document began as the Stage 11.0 cloud deployment plan and guardrails. It now also records the manually validated Stage 11.2 through 11.4 cloud-hosted portfolio deployment evidence.

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
| GitHub deployment identity | `id-github-mlops-churn` | Intended federated deployment identity. |

The workload resource names were validated during manual deployment. The GitHub deployment identity remains planned for Stage 11.5 and has not yet been created or configured by this documentation step.

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

## Cost Guardrails

- Use the existing billing budget `budget-mlops-portfolio`.
- Keep the monthly budget at £10.
- Keep actual-cost alerts at 50%, 80% and 100%.
- Deploy only resources required for the cloud MVP and prefer low-cost or consumption-based configuration where practical.
- Review Azure Cost Management and remaining student credit during deployment validation and again after teardown.
- Remove cloud runtime resources after the required evidence is collected when a live endpoint is no longer needed.
- Keep the £10 billing budget as an account-level guardrail unless it is explicitly removed later.

A budget and alerts help detect spend but do not automatically stop or delete Azure resources.

## Deployment Identity and Least Privilege

GitHub Actions deployment must use OIDC federation rather than a long-lived Azure client secret or password. Pull request workflows must never deploy Azure resources.

Deployment permissions should be scoped as narrowly as practical to `rg-mlops-churn-portfolio` and to the actions required by the selected deployment process. Subscription-wide Owner access must not be granted for normal CI/CD deployment. Role assignments should be reviewed before use and removed during teardown when they are no longer required.

## Secret-Handling Policy

- Do not commit Azure credentials, access keys, passwords, tokens or generated credential files to Git.
- Do not create a long-lived Azure client secret for GitHub Actions.
- Store only non-secret identifiers required by OIDC configuration in GitHub repository or environment configuration.
- Treat subscription, tenant and client identifiers as configuration metadata and avoid exposing them unnecessarily in reports or screenshots.
- Use GitHub environment protections for deployment where practical.
- Redact sensitive values from terminal output, screenshots and portfolio evidence.
- Prefer Azure identity and role-based access control over registry admin credentials or embedded passwords.

## Cloud Build Artifact Guardrail

The validated `model_pipeline.joblib` remains outside Git. Its provenance, runtime compatibility and authoritative SHA-256 checksum are recorded in `deployment/model_artifact.json`. The `model-v1.0.0` GitHub Release has been published with the `model_pipeline.joblib` asset, and GitHub reports the same SHA-256 as the manifest. Real clean-runner/network retrieval is the next validation step and has not yet been completed. No Azure runtime or workload resources were provisioned by publishing the release.

Before any future Docker build on a clean runner, the pinned release asset must be downloaded to a temporary file and verified against the manifest checksum. It may only be installed at `artifacts/model_pipeline.joblib` after verification succeeds. Deployment builds must never load an unverified joblib/pickle artifact. This foundation does not provision Azure runtime resources or add deployment automation.

## Explicitly Out of Scope

The Stage 11 cloud MVP does not include:

- GitHub Actions deployment workflows before Stage 11.5;
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
6. Next: configure GitHub OIDC federation and narrowly scoped deployment permissions in Stage 11.5.
7. Next: add a deployment workflow that cannot deploy from pull request events and validate the intended CI/CD path.
8. Later: collect final portfolio evidence and follow `docs/azure_teardown_checklist.md` when a live endpoint is no longer required.
