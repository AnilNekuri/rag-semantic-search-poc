# AWS RAG Semantic Search POC

## Project Name

`aws-rag-document-semantic-search-poc`

## Goal

Build a small AWS-based semantic search POC where a PDF is uploaded to S3, text is extracted using Amazon Textract, embeddings are generated using Amazon Bedrock, and the document chunks are indexed into Amazon OpenSearch Serverless Vector Search.

The first version will stop at **semantic retrieval**.

This means:

```text
User question
   ↓
Bedrock embedding
   ↓
OpenSearch Serverless vector query
   ↓
Top matching document chunks
```

Later, this can be extended into full RAG by sending the retrieved chunks to a Bedrock LLM for answer generation.

---

## Initial Scope

### Included

1. Upload PDF to Amazon S3
2. Extract text from PDF using Amazon Textract
3. Split extracted text into chunks
4. Generate embeddings using Amazon Bedrock
5. Store chunks and vectors in OpenSearch Serverless
6. Query OpenSearch using an embedded user question
7. Return top matching chunks

### Not Included in First Version

- API Gateway
- Lambda automation
- Step Functions
- Bedrock final answer generation
- Frontend UI
- Authentication
- Production security hardening

These can be added later.

---

## Architecture

```text
PDF Document
   ↓
Amazon S3
   ↓
Amazon Textract
   ↓
Extracted Text
   ↓
Text Chunking
   ↓
Amazon Bedrock Titan Embeddings
   ↓
OpenSearch Serverless Vector Index
   ↓
Question Embedding
   ↓
Vector Search
   ↓
Top Matching Chunks
```

---

## AWS Services

| Purpose | AWS Service |
|---|---|
| PDF storage | Amazon S3 |
| OCR / text extraction | Amazon Textract |
| Embeddings | Amazon Bedrock |
| Vector database | Amazon OpenSearch Serverless |
| Metadata storage | OpenSearch document fields |
| Monitoring | CloudWatch |
| Security | IAM |

---

## Important Concept

You cannot query OpenSearch vector search directly using plain English against the vector field.

You must first convert the user question into an embedding using the same Bedrock embedding model used during indexing.

Correct flow:

```text
"What is the reason for this dispute?"
   ↓
Bedrock Titan Embeddings
   ↓
Question vector
   ↓
OpenSearch k-NN query
   ↓
Relevant document chunks
```

---

## Suggested Folder Structure

```text
aws-rag-document-semantic-search-poc/
│
├── README.md
├── requirements.txt
├── .env.example
│
├── scripts/
│   ├── 01_upload_pdf.py
│   ├── 02_extract_text_textract.py
│   ├── 03_chunk_text.py
│   ├── 04_generate_embeddings.py
│   ├── 05_create_opensearch_index.py
│   ├── 06_index_chunks.py
│   └── 07_query_opensearch.py
│
├── data/
│   ├── sample-pdfs/
│   ├── extracted-text/
│   └── chunks/
│
└── docs/
    └── architecture.md
```

---

## Environment Variables

Create a `.env` file locally.

```bash
AWS_REGION=us-east-1

S3_BUCKET_NAME=aws-rag-poc-documents
S3_INPUT_PREFIX=input/

BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v2:0

OPENSEARCH_COLLECTION_ENDPOINT=https://your-collection-endpoint.us-east-1.aoss.amazonaws.com
OPENSEARCH_INDEX_NAME=claims-rag-index
```

---

## Python Dependencies

Example `requirements.txt`:

```txt
boto3
botocore
opensearch-py
requests-aws4auth
python-dotenv
tiktoken
```

If `tiktoken` causes issues, start with simple character-based chunking first.

---

## Step 1: Upload PDF to S3

Use S3 to store the source PDF.

Example path:

```text
s3://aws-rag-poc-documents/input/claim_1001.pdf
```

Script:

```text
scripts/01_upload_pdf.py
```

Expected result:

```text
PDF uploaded successfully to S3.
```

---

## Step 2: Extract Text using Textract

For the first version, use:

```text
StartDocumentTextDetection
```

This is enough for basic OCR/text extraction.

Later, if you need forms or tables, use:

```text
StartDocumentAnalysis
```

Output example:

```json
{
  "document_id": "claim_1001",
  "s3_key": "input/claim_1001.pdf",
  "pages": [
    {
      "page_number": 1,
      "text": "Extracted text from page 1..."
    }
  ]
}
```

Save extracted text locally under:

```text
data/extracted-text/claim_1001.json
```

---

## Step 3: Chunk Extracted Text

Split the extracted text into smaller chunks.

Recommended first version:

```text
chunk_size = 1000 characters
chunk_overlap = 150 characters
```

Later, improve using token-based chunking.

Chunk output example:

```json
{
  "chunk_id": "claim_1001_page_1_chunk_1",
  "document_id": "claim_1001",
  "page_number": 1,
  "s3_key": "input/claim_1001.pdf",
  "text": "This is the extracted chunk text..."
}
```

---

## Step 4: Generate Bedrock Embeddings

Use Bedrock Titan Embeddings.

Recommended model:

```text
amazon.titan-embed-text-v2:0
```

Recommended dimension for first POC:

```text
1024
```

Each text chunk should produce one embedding vector.

Example output:

```json
{
  "chunk_id": "claim_1001_page_1_chunk_1",
  "text": "This is the extracted chunk text...",
  "embedding": [0.0123, -0.0456, 0.0789]
}
```

---

## Step 5: Create OpenSearch Serverless Vector Index

Create an OpenSearch index with a vector field.

Example mapping:

```json
{
  "settings": {
    "index": {
      "knn": true
    }
  },
  "mappings": {
    "properties": {
      "chunk_id": {
        "type": "keyword"
      },
      "document_id": {
        "type": "keyword"
      },
      "claim_id": {
        "type": "keyword"
      },
      "document_type": {
        "type": "keyword"
      },
      "page_number": {
        "type": "integer"
      },
      "s3_key": {
        "type": "keyword"
      },
      "text": {
        "type": "text"
      },
      "embedding": {
        "type": "knn_vector",
        "dimension": 1024,
        "method": {
          "name": "hnsw",
          "engine": "faiss",
          "space_type": "cosinesimil"
        }
      }
    }
  }
}
```

Important: The `dimension` must match the embedding dimension returned by Bedrock.

---

## Step 6: Index Chunks into OpenSearch

Each OpenSearch document should contain:

```json
{
  "chunk_id": "claim_1001_page_1_chunk_1",
  "document_id": "claim_1001",
  "claim_id": "1001",
  "document_type": "claim_pdf",
  "page_number": 1,
  "s3_key": "input/claim_1001.pdf",
  "text": "Extracted text chunk...",
  "embedding": [0.0123, -0.0456, 0.0789]
}
```

Expected result:

```text
Indexed 25 chunks into OpenSearch.
```

---

## Step 7: Query OpenSearch

User question:

```text
What is the reason for the claim dispute?
```

Processing flow:

```text
Question
   ↓
Bedrock embedding
   ↓
OpenSearch vector query
   ↓
Top 5 matching chunks
```

Example vector query:

```json
{
  "size": 5,
  "query": {
    "knn": {
      "embedding": {
        "vector": [0.0123, -0.0456, 0.0789],
        "k": 5
      }
    }
  }
}
```

Expected output:

```json
[
  {
    "score": 0.91,
    "chunk_id": "claim_1001_page_2_chunk_1",
    "page_number": 2,
    "text": "The provider disputed the allowed amount because..."
  },
  {
    "score": 0.87,
    "chunk_id": "claim_1001_page_3_chunk_2",
    "page_number": 3,
    "text": "Supporting documentation submitted by the provider..."
  }
]
```

---

## Good Test Questions

Use these questions for your first demo:

```text
What is the reason for this dispute?
Which document mentions the provider billed amount?
What claim number is associated with this document?
What supporting documents were submitted?
Is this related to ONR or IDR?
Summarize the key information from the retrieved chunks.
Find text related to anesthesia pricing.
Find text related to air ambulance service.
Find missing claim or service code details.
```

---

## First Milestone

Complete this:

```text
One PDF uploaded to S3
Textract extracts text
Text is chunked
Chunks are embedded using Bedrock
Chunks are stored in OpenSearch Serverless
A user question is embedded
OpenSearch returns top 5 similar chunks
```

This proves the core semantic search flow.

---

## Later Enhancements

After the small version works, add:

1. Lambda trigger from S3 upload
2. Step Functions workflow
3. DynamoDB metadata table
4. API Gateway endpoint
5. Bedrock LLM answer generation
6. Source citation with document name and page number
7. Hybrid search: keyword + vector + metadata filters
8. CloudWatch logging and tracing
9. CI/CD with GitHub Actions or GitLab
10. Production-ready Terraform modules and remote state

---

## Full RAG Extension

Later flow:

```text
User question
   ↓
Bedrock embedding
   ↓
OpenSearch retrieves top chunks
   ↓
Chunks are added to LLM prompt
   ↓
Bedrock LLM generates final answer
   ↓
Answer includes source document and page references
```

Example final answer:

```text
The dispute appears to be related to the allowed amount for the anesthesia claim.
The retrieved supporting text mentions billed amount, service code, and provider-submitted documentation.

Sources:
- claim_1001.pdf, page 2
- provider_letter_1001.pdf, page 1
```

---

## Resume Bullet After Completion

Use this after the POC is working:

```text
Built an AWS-based semantic search POC using S3, Amazon Textract, Bedrock Titan Embeddings, and OpenSearch Serverless vector search to retrieve relevant chunks from OCR-extracted PDF documents.
```

Stronger version:

```text
Designed and built an AWS RAG-ready document intelligence POC using S3, Amazon Textract, Bedrock embeddings, and OpenSearch Serverless vector search to enable semantic retrieval across OCR-extracted claim and dispute documents.
```

---

## GitHub README Summary

```text
This project demonstrates an AWS-based RAG-ready semantic search pipeline. It extracts text from PDF documents using Amazon Textract, generates vector embeddings using Amazon Bedrock Titan Embeddings, stores vectors in Amazon OpenSearch Serverless, and performs semantic search by embedding user questions and retrieving the most relevant document chunks.
```

---

## Terraform Infrastructure Plan

We will use Terraform for the first AWS infrastructure pass, while keeping the application flow local-script based.

### Terraform Scope

Create only the core infrastructure needed for the POC:

1. S3 bucket for source PDFs
2. OpenSearch Serverless vector search collection
3. IAM permissions for local scripts
4. Terraform outputs for `.env` values

Do not include Lambda, Step Functions, API Gateway, frontend UI, or final Bedrock answer generation in the first Terraform pass.

### Defaults

```text
AWS region: us-east-2
AWS CLI profile: anekur-admin
Bedrock embedding model: amazon.titan-embed-text-v2:0
OpenSearch index name: claims-rag-index
```

### Planned Terraform Folder

```text
infra/
  terraform/
    versions.tf
    providers.tf
    variables.tf
    main.tf
    outputs.tf
    terraform.tfvars.example
```

### Terraform Resources

1. Configure the AWS provider for `us-east-2` and profile `anekur-admin`.
2. Create a private S3 bucket with encryption and versioning.
3. Create OpenSearch Serverless security policies:
   - Encryption policy
   - Network policy
   - Data access policy
4. Create an OpenSearch Serverless `VECTORSEARCH` collection.
5. Use dev/test cost settings where possible, including disabled standby replicas.
6. Create IAM policy permissions for:
   - S3 upload and read
   - Textract `StartDocumentTextDetection` and result polling
   - Bedrock `InvokeModel` for embeddings
   - OpenSearch Serverless API access
7. Output:
   - S3 bucket name
   - OpenSearch collection endpoint
   - OpenSearch collection ARN
   - AWS region
   - Suggested `.env` values

### Important Cost Note

OpenSearch Serverless is the main cost risk.

Approximate POC cost:

```text
Short test, then terraform destroy: usually under $5
OpenSearch dev/test left running all month: about $175/month
OpenSearch HA left running all month: about $350/month
```

Run this after testing:

```powershell
terraform destroy
```

### Terraform Execution Steps

```powershell
aws sso login --profile anekur-admin
aws sts get-caller-identity --profile anekur-admin

cd infra/terraform
terraform init
terraform fmt
terraform validate
terraform plan
terraform apply
```

Terraform is not currently installed on this machine, so install Terraform or add it to `PATH` before running these commands.

### After Terraform

Use the Terraform outputs to create the local `.env` file, then build the Python scripts in order:

1. Upload PDF to S3
2. Extract text with Textract
3. Chunk extracted text
4. Generate Bedrock embeddings
5. Create OpenSearch vector index
6. Index embedded chunks
7. Query OpenSearch with an embedded user question

---

## Recommended Build Order for Codex

Ask Codex to generate one script at a time.

Suggested prompts:

### Prompt 1

```text
Create a Python script to upload a local PDF file to an S3 bucket using boto3. Read bucket name and region from environment variables.
```

### Prompt 2

```text
Create a Python script that starts Amazon Textract StartDocumentTextDetection for a PDF stored in S3, polls until completion, extracts LINE text by page, and saves output as JSON.
```

### Prompt 3

```text
Create a Python utility to split extracted page text into overlapping chunks. Each chunk should include chunk_id, document_id, page_number, s3_key, and text.
```

### Prompt 4

```text
Create a Python script to call Amazon Bedrock Titan Text Embeddings V2 for each text chunk and add the embedding array to each chunk.
```

### Prompt 5

```text
Create a Python script to create an OpenSearch Serverless vector index with a knn_vector field named embedding and dimension 1024.
```

### Prompt 6

```text
Create a Python script to bulk index embedded chunks into OpenSearch Serverless using AWS SigV4 authentication.
```

### Prompt 7

```text
Create a Python script that accepts a natural-language question, generates a Bedrock embedding for the question, queries OpenSearch Serverless using k-NN vector search, and prints the top 5 matching chunks with scores and metadata.
```

---

## Notes

- Use synthetic/sample PDFs only.
- Do not use real client, patient, claim, or employer data.
- Keep the first version local-script based.
- Add Lambda and Step Functions only after the local flow works.
- Keep the POC simple and working before adding production-style features.
