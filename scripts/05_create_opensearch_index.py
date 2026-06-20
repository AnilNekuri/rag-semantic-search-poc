from common import load_settings, opensearch_client


def main() -> None:
    settings = load_settings()
    client = opensearch_client(settings)
    index_name = settings["opensearch_index_name"]

    if client.indices.exists(index=index_name):
        print(f"Index already exists: {index_name}")
        return

    mapping = {
        "settings": {
            "index": {
                "knn": True,
            }
        },
        "mappings": {
            "properties": {
                "chunk_id": {"type": "keyword"},
                "document_id": {"type": "keyword"},
                "claim_id": {"type": "keyword"},
                "document_type": {"type": "keyword"},
                "page_number": {"type": "integer"},
                "s3_key": {"type": "keyword"},
                "text": {"type": "text"},
                "embedding": {
                    "type": "knn_vector",
                    "dimension": 1024,
                    "method": {
                        "name": "hnsw",
                        "engine": "faiss",
                        "space_type": "cosinesimil",
                    },
                },
            }
        },
    }

    client.indices.create(index=index_name, body=mapping)
    print(f"Created OpenSearch index: {index_name}")


if __name__ == "__main__":
    main()
