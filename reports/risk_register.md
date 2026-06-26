# Risk Register

This risk register tracks initial project risks for the Telco customer churn MLOps prototype.

| Risk ID | Risk | Description | Potential impact | Mitigation | Status |
|---|---|---|---|---|---|
| R001 | Data drift | Incoming customer profiles may differ from the training data distribution. | Model performance may degrade over time. | Add simulated drift detection and document feature shift scenarios. | Open |
| R002 | Over-reliance on churn probability | Users may treat churn probability as a definitive decision rather than an estimate. | Customers may receive inappropriate or unfair treatment. | Position predictions as decision support and require human review. | Open |
| R003 | False positives | The model may incorrectly flag customers as likely to churn. | Unnecessary retention actions, wasted resources or poor customer experience. | Track precision, review threshold choice and include human review guidance. | Open |
| R004 | False negatives | The model may miss customers who are likely to churn. | Missed retention opportunities and misleading confidence in model coverage. | Track recall, confusion matrix and threshold tradeoffs. | Open |
| R005 | Dataset representativeness | The public dataset may not represent a real company's customer base. | Evaluation results may not generalise to real business settings. | Document dataset limitations and avoid claims of production impact. | Open |
| R006 | Simulated monitoring limits | Simulated monitoring is not equivalent to real production monitoring. | Monitoring outputs may overstate production readiness. | Clearly label drift detection as simulated and local to this portfolio project. | Open |
| R007 | Privacy concerns if applied to real customer data | Real customer data could contain sensitive personal or billing information. | Privacy, compliance and trust risks. | Do not include real customer data; document privacy review needs for any real deployment. | Open |
