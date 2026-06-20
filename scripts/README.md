# Local Pipeline Scripts

Run these scripts from the project root after Terraform has been applied and `.env` has been created.

Install dependencies first:

```powershell
python -m pip install -r requirements.txt
```

## 1. Upload PDF

```powershell
python scripts/01_upload_pdf.py data/sample-pdfs/sample.pdf
```

The script prints the S3 key, for example:

```text
input/sample.pdf
```

## 2. Extract Text With Textract

```powershell
python scripts/02_extract_text_textract.py input/sample.pdf
```

Output:

```text
data/extracted-text/sample.json
```

## 3. Chunk Text

```powershell
python scripts/03_chunk_text.py sample.json
```

Output:

```text
data/chunks/sample.json
```

## 4. Generate Embeddings

```powershell
python scripts/04_generate_embeddings.py sample.json
```

Output:

```text
data/embedded-chunks/sample.json
```

## 5. Create OpenSearch Index

```powershell
python scripts/05_create_opensearch_index.py
```

## 6. Index Chunks

```powershell
python scripts/06_index_chunks.py sample.json
```

## 7. Query OpenSearch

```powershell
python scripts/07_query_opensearch.py "What is the reason for this dispute?"
```
