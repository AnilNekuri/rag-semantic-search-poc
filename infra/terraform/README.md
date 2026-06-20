# Terraform Setup

This folder contains the Terraform configuration for the AWS RAG semantic search POC.

## Defaults

```text
Region: us-east-2
AWS profile: anekur-admin
State: local Terraform state
```

Terraform is intentionally using local state for the first POC pass.

## Current Resources

The current Terraform configuration creates:

- Private S3 bucket for source PDFs
- S3 public access block
- S3 bucket owner enforced object ownership
- S3 SSE-S3 encryption
- S3 bucket versioning
- OpenSearch Serverless encryption policy
- OpenSearch Serverless public network policy for POC access
- OpenSearch Serverless `VECTORSEARCH` collection with standby replicas disabled
- Optional OpenSearch Serverless data access policy when `aoss_data_access_principal_arns` is set
- IAM policy for local scripts to use S3, Textract, Bedrock embeddings, and OpenSearch Serverless
- Optional IAM policy attachments when `poc_iam_role_names_to_attach` is set

The bucket uses `s3_force_destroy = true` by default so `terraform destroy` can delete the bucket and all POC objects inside it.

## First-Time Commands

```powershell
aws sso login --profile anekur-admin
aws sts get-caller-identity --profile anekur-admin

cd infra/terraform
terraform init
terraform fmt
terraform validate
terraform plan
```

Terraform is not currently installed on this machine's `PATH`, so install Terraform before running these commands.

## Local Variables

Copy the example file if you need local overrides:

```powershell
Copy-Item terraform.tfvars.example terraform.tfvars
```

Do not commit `terraform.tfvars`, state files, plans, or credentials.
