import hashlib

from common import (
    EMBEDDED_CHUNKS_DIR,
    QUERY_EMBEDDINGS_DIR,
    bedrock_embed_text,
    boto3_client,
    ensure_dirs,
    load_settings,
    opensearch_client,
    parse_args,
    read_json,
    write_json,
)


def query_cache_path(question: str) -> str:
    digest = hashlib.sha256(question.strip().lower().encode("utf-8")).hexdigest()
    return QUERY_EMBEDDINGS_DIR / f"{digest}.json"


def embed_question(settings: dict, question: str, use_cache: bool = True) -> list[float]:
    cache_path = query_cache_path(question)
    if use_cache and cache_path.exists():
        cached = read_json(cache_path)
        print(f"Using cached question embedding: {cache_path}")
        return cached["embedding"]

    print(f"Generating question embedding with Bedrock in {settings['bedrock_region']}...")
    bedrock_runtime = boto3_client(settings, "bedrock-runtime", max_attempts=1)
    embedding = bedrock_embed_text(bedrock_runtime, settings["bedrock_embedding_model_id"], question)
    if use_cache:
        write_json(
            cache_path,
            {
                "question": question,
                "model_id": settings["bedrock_embedding_model_id"],
                "embedding": embedding,
            },
        )
        print(f"Saved question embedding cache: {cache_path}")
    return embedding


def load_first_local_vector(embedded_chunks_json: str) -> list[float]:
    path = EMBEDDED_CHUNKS_DIR / embedded_chunks_json
    chunks = read_json(path)
    if not chunks:
        raise RuntimeError(f"No chunks found in {path}")
    print(f"Using first local chunk embedding as test vector: {path}")
    return chunks[0]["embedding"]


def main() -> None:
    parser = parse_args("Embed a question and retrieve top matching chunks from OpenSearch.")
    parser.add_argument("question", help="Natural-language search question.")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--no-cache", action="store_true", help="Always call Bedrock instead of reusing a cached question embedding.")
    parser.add_argument(
        "--test-with-local-vector",
        help="Skip Bedrock and query OpenSearch with the first embedding from data/embedded-chunks/<file>. This proves OpenSearch search works, but is not a real question embedding.",
    )
    args = parser.parse_args()

    settings = load_settings()
    ensure_dirs()
    client = opensearch_client(settings)
    if args.test_with_local_vector:
        vector = load_first_local_vector(args.test_with_local_vector)
    else:
        vector = embed_question(settings, args.question, use_cache=not args.no_cache)

    print(f"Querying OpenSearch index: {settings['opensearch_index_name']}...")
    response = client.search(
        index=settings["opensearch_index_name"],
        body={
            "size": args.top_k,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": vector,
                        "k": args.top_k,
                    }
                }
            },
        },
    )

    hits = response.get("hits", {}).get("hits", [])
    for index, hit in enumerate(hits, start=1):
        source = hit["_source"]
        print(f"\n#{index} score={hit['_score']}")
        print(f"chunk_id: {source.get('chunk_id')}")
        print(f"document_id: {source.get('document_id')}")
        print(f"page_number: {source.get('page_number')}")
        print(f"s3_key: {source.get('s3_key')}")
        print(source.get("text", "")[:1000])


if __name__ == "__main__":
    main()
