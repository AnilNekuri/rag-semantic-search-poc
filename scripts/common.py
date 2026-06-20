import argparse
import json
import os
import random
import time
from pathlib import Path
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from dotenv import load_dotenv
from opensearchpy import AWSV4SignerAuth, OpenSearch, RequestsHttpConnection


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
EXTRACTED_TEXT_DIR = DATA_DIR / "extracted-text"
CHUNKS_DIR = DATA_DIR / "chunks"
EMBEDDED_CHUNKS_DIR = DATA_DIR / "embedded-chunks"
QUERY_EMBEDDINGS_DIR = DATA_DIR / "query-embeddings"


def load_settings() -> dict:
    load_dotenv(PROJECT_ROOT / ".env")

    required = [
        "AWS_REGION",
        "S3_BUCKET_NAME",
        "S3_INPUT_PREFIX",
        "BEDROCK_EMBEDDING_MODEL_ID",
        "OPENSEARCH_COLLECTION_ENDPOINT",
        "OPENSEARCH_INDEX_NAME",
    ]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    return {
        "aws_region": os.environ["AWS_REGION"],
        "bedrock_region": os.getenv("BEDROCK_REGION", os.environ["AWS_REGION"]),
        "aws_profile": os.getenv("AWS_PROFILE"),
        "s3_bucket_name": os.environ["S3_BUCKET_NAME"],
        "s3_input_prefix": os.environ["S3_INPUT_PREFIX"].strip("/"),
        "bedrock_embedding_model_id": os.environ["BEDROCK_EMBEDDING_MODEL_ID"],
        "opensearch_collection_endpoint": os.environ["OPENSEARCH_COLLECTION_ENDPOINT"],
        "opensearch_index_name": os.environ["OPENSEARCH_INDEX_NAME"],
    }


def boto3_session(settings: dict) -> boto3.Session:
    return boto3.Session(
        profile_name=settings["aws_profile"] or None,
        region_name=settings["aws_region"],
    )


def boto3_client(settings: dict, service_name: str, max_attempts: int = 10):
    session = boto3_session(settings)
    region_name = settings["bedrock_region"] if service_name == "bedrock-runtime" else settings["aws_region"]
    return session.client(
        service_name,
        region_name=region_name,
        config=Config(
            connect_timeout=10,
            read_timeout=30,
            retries={"max_attempts": max_attempts, "mode": "standard"},
        ),
    )


def bedrock_embed_text(
    bedrock_runtime,
    model_id: str,
    text: str,
    dimensions: int = 1024,
    max_attempts: int = 8,
) -> list[float]:
    body = json.dumps(
        {
            "inputText": text,
            "dimensions": dimensions,
            "normalize": True,
        }
    )

    for attempt in range(1, max_attempts + 1):
        try:
            response = bedrock_runtime.invoke_model(
                modelId=model_id,
                body=body,
                contentType="application/json",
                accept="application/json",
            )
            payload = json.loads(response["body"].read())
            return payload["embedding"]
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code", "")
            if error_code not in {"ThrottlingException", "TooManyRequestsException"} or attempt == max_attempts:
                raise

            sleep_seconds = min(2 ** attempt, 30) + random.uniform(0, 1)
            print(f"Bedrock throttled request; retrying in {sleep_seconds:.1f}s ({attempt}/{max_attempts})")
            time.sleep(sleep_seconds)

    raise RuntimeError("Bedrock embedding failed after retries.")


def ensure_dirs() -> None:
    EXTRACTED_TEXT_DIR.mkdir(parents=True, exist_ok=True)
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    EMBEDDED_CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    QUERY_EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)


def document_id_from_path(path: Path) -> str:
    return path.stem.replace(" ", "_")


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args(description: str) -> argparse.ArgumentParser:
    return argparse.ArgumentParser(description=description)


def opensearch_host(endpoint: str) -> str:
    parsed = urlparse(endpoint)
    return parsed.netloc or parsed.path


def opensearch_client(settings: dict) -> OpenSearch:
    session = boto3_session(settings)
    credentials = session.get_credentials()
    auth = AWSV4SignerAuth(credentials, settings["aws_region"], "aoss")

    return OpenSearch(
        hosts=[{"host": opensearch_host(settings["opensearch_collection_endpoint"]), "port": 443}],
        http_auth=auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        timeout=60,
    )
