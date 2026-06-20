# Terraform POC Plan

Here is the plan in simple steps.

## 1. Set Up Terraform

Create `infra/terraform/` with provider config, variables, outputs, and local state.

## 2. Use AWS SSO

Standardize on:

```text
Region: us-east-2
Profile: anekur-admin
```

## 3. Create S3 Bucket

Store uploaded PDF files privately with encryption and versioning.

## 4. Create OpenSearch Serverless

Provision a `VECTORSEARCH` collection for semantic search.

## 5. Keep Cost Low

Use dev/test mode with standby replicas disabled, and destroy infra when done.

## 6. Create IAM Permissions

Allow local scripts to use:

- S3
- Textract
- Bedrock embeddings
- OpenSearch Serverless

## 7. Output Connection Values

Terraform should print:

- S3 bucket name
- OpenSearch endpoint
- Region
- Values for `.env`

## 8. Build Python Scripts After Infra

Scripts will:

- Upload PDF
- Extract text with Textract
- Chunk text
- Generate Bedrock embeddings
- Create OpenSearch index
- Index chunks
- Query top matches

## 9. Test With One Synthetic PDF

Confirm one question returns top matching chunks.

## 10. Clean Up

Run this after testing so OpenSearch does not keep charging monthly:

```powershell
terraform destroy
```
