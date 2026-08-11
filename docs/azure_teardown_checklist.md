# Azure Teardown Checklist

Use this checklist after Stage 11 cloud MVP evidence has been collected and a live endpoint is no longer required. All items are intentionally unchecked; this document does not claim that any Azure resource has been deleted.

## Preserve Evidence

- [ ] Confirm that required deployment, API validation, observability and cost evidence has been saved locally or in GitHub as appropriate.
- [ ] Review screenshots and reports for credentials, tokens, access keys or other sensitive values before retaining them.
- [ ] Confirm that raw data, runtime logs, `mlruns/` and model artifacts have not been committed to Git.

## Inventory Before Deletion

- [ ] Confirm the active subscription is `Azure for Students`.
- [ ] List every resource in `rg-mlops-churn-portfolio` and record anything that does not match the approved Stage 11 scope.
- [ ] Check for locks, role assignments, federated credentials, diagnostic settings and dependent resources that may affect deletion.
- [ ] Record the current Azure credit balance and Cost Management view before teardown.

## Remove Project Resources

- [ ] Delete the Container App `ca-mlops-churn-api` when the live endpoint is no longer required.
- [ ] Delete the Container Apps Environment `cae-mlops-churn` after its container apps are removed.
- [ ] Delete the Azure Container Registry used by the project after required image evidence is retained.
- [ ] Delete the Log Analytics Workspace `log-mlops-churn` after required log evidence is retained.
- [ ] Remove the GitHub federated credential and project deployment role assignments.
- [ ] Delete the GitHub deployment identity `id-github-mlops-churn` when it is no longer required.
- [ ] Delete any other project resource found in `rg-mlops-churn-portfolio` after confirming that it belongs to this portfolio deployment.

## Remove the Resource Group

- [ ] Confirm that no required project resources or evidence remain only in Azure.
- [ ] Delete `rg-mlops-churn-portfolio` after its contained resources are no longer required.
- [ ] Wait for resource-group deletion to complete and verify that the group no longer appears in Azure Resource Groups.
- [ ] Check for any Azure Container Apps managed or infrastructure resource group and delete it if it remains and is confirmed to belong to this project.

## Post-Teardown Verification

- [ ] Recheck Azure Resource Groups for project or managed resource groups left behind.
- [ ] Recheck the Azure Container Apps, Container Registry, Log Analytics and managed identity resource lists for project resources.
- [ ] Recheck GitHub environment or repository configuration and remove deployment configuration that is no longer needed.
- [ ] Recheck Azure Cost Management for continuing or delayed project charges.
- [ ] Recheck the Azure for Students credit balance after Azure cost data has updated.
- [ ] Keep the £10 billing budget `budget-mlops-portfolio` as an account-level guardrail unless it is explicitly removed later.
- [ ] Record the teardown date, verification evidence and any delayed charges in the project documentation without claiming completion before verification.
