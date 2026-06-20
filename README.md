# AWS RAG Semantic Search POC

This project is a small AWS-based semantic search proof of concept.

It uploads synthetic PDFs to S3, extracts text with Amazon Textract, generates embeddings with Amazon Bedrock Titan Embeddings, stores vectors in Amazon OpenSearch Serverless, and queries the most relevant document chunks.

The first version stops at semantic retrieval. It does not generate final LLM answers yet.

## Architecture

```text
PDF
  -> S3
  -> Textract
  -> extracted text
  -> chunks
  -> Bedrock Titan embeddings
  -> OpenSearch Serverless vector index
  -> question embedding
  -> top matching chunks
```

## Prerequisites

- Python 3.12+
- Terraform
- AWS CLI
- AWS profile with access to S3, Textract, Bedrock, IAM, and OpenSearch Serverless

The local setup used for this POC:

```text
AWS region: us-east-2
Bedrock region: us-east-1
AWS profile: anekur-admin
```

## Terraform Infrastructure

Terraform lives in:

```text
infra/terraform
```

It creates:

- S3 bucket for PDF uploads
- OpenSearch Serverless `VECTORSEARCH` collection
- OpenSearch Serverless security and access policies
- IAM policy for local POC scripts
- outputs for local `.env` configuration

Run:

```powershell
cd infra\terraform
terraform init
terraform fmt
terraform validate
terraform plan
terraform apply
```

After apply, create `.env` from the Terraform output:

```powershell
terraform output -raw env_file_text
```

Use `.env.example` as the template.

## Cost Warning

OpenSearch Serverless is the main cost risk. It can cost money while idle.

For this POC, standby replicas are disabled, and the S3 bucket is configured with `force_destroy = true` so the infrastructure can be deleted cleanly.

Destroy resources when done testing:

```powershell
cd infra\terraform
terraform destroy
```

## Local Python Setup

From the project root:

```powershell
python -m pip install -r requirements.txt
```

## Test Pipeline

Use one synthetic PDF:

```text
data/sample-pdfs/synthetic-claim-dispute.pdf
```

Run:

```powershell
python scripts/01_upload_pdf.py data/sample-pdfs/synthetic-claim-dispute.pdf
python scripts/02_extract_text_textract.py input/synthetic-claim-dispute.pdf
python scripts/03_chunk_text.py synthetic-claim-dispute.json
python scripts/04_generate_embeddings.py synthetic-claim-dispute.json
python scripts/05_create_opensearch_index.py
python scripts/06_index_chunks.py synthetic-claim-dispute.json
python scripts/07_query_opensearch.py "What is the reason for this dispute?"
```

If Bedrock throttles during query testing, verify OpenSearch search with the locally generated vector:

```powershell
python scripts/07_query_opensearch.py "test" --test-with-local-vector synthetic-claim-dispute.json
```

## Notes

- Use synthetic/sample PDFs only.
- Do not use real client, patient, claim, employer, or confidential data.
- Do not commit `.env`, Terraform state, credentials, or generated data.
- Full RAG answer generation can be added later by sending retrieved chunks to a Bedrock LLM.
