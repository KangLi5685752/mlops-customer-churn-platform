# Azure Deployment Plan

## Status

This document defines the Stage 11.0 cloud deployment plan and guardrails. It does not record a completed cloud deployment.

The Azure resource group `rg-mlops-churn-portfolio` has been created in UK South and currently contains no deployed resources. The project remains a cost-controlled portfolio cloud deployment MVP.

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

All project resources should use `UK South` where the selected service supports it. Keeping the MVP in one region simplifies cost review, resource discovery and teardown.

## Resource Naming

| Resource | Intended name | Notes |
| --- | --- | --- |
| Resource Group | `rg-mlops-churn-portfolio` | Created successfully; currently contains no deployed resources. |
| Azure Container Registry | `acrmlopschurnkl5685752` | Availability must be checked at creation time because ACR names are globally unique. |
| Container Apps Environment | `cae-mlops-churn` | Intended environment for the API container app. |
| Container App | `ca-mlops-churn-api` | Intended public API runtime. |
| Log Analytics Workspace | `log-mlops-churn` | Intended platform logging workspace. |
| GitHub deployment identity | `id-github-mlops-churn` | Intended federated deployment identity. |

Names are frozen for planning purposes, except that the ACR name may require revision if it is unavailable when creation is attempted. Any revision should be recorded before deployment automation is added.

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

## Explicitly Out of Scope

Stage 11.0 does not implement or add:

- Azure resources beyond the already-created empty resource group;
- deployment code or GitHub Actions deployment workflows;
- changes to the Docker application or model workflow;
- Terraform or Bicep;
- Kubernetes or AKS;
- Databricks or Spark;
- databases, authentication or unrelated infrastructure;
- enterprise production deployment claims, production traffic, production SLAs or real customer impact.

## Intended Stage 11 Sequence

1. Stage 11.0: record Azure scope, names, security decisions, cost controls and teardown requirements.
2. Validate the Azure subscription context, UK South service availability, required providers and global availability of the planned ACR name.
3. Create only the approved ACR, Log Analytics and Container Apps resources within `rg-mlops-churn-portfolio` using cost-conscious settings.
4. Build and publish the existing API image without committing the raw dataset or local model artifacts to Git.
5. Deploy the container app and validate `/health`, `/docs` and `/predict` with synthetic requests.
6. Configure `id-github-mlops-churn` with GitHub OIDC federation and narrowly scoped resource-group deployment permissions.
7. Add a deployment workflow that cannot deploy from pull request events, then validate the intended CI/CD path.
8. Collect cost, deployment and basic observability evidence using careful portfolio wording.
9. Follow `docs/azure_teardown_checklist.md` when a live endpoint is no longer required, then verify remaining resources and costs.

Each later step requires separate implementation and validation. None of those steps is marked complete by this plan.
