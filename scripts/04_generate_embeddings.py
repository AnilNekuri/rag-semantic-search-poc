from pathlib import Path

from common import (
    CHUNKS_DIR,
    EMBEDDED_CHUNKS_DIR,
    bedrock_embed_text,
    boto3_client,
    ensure_dirs,
    load_settings,
    parse_args,
    read_json,
    write_json,
)


def main() -> None:
    parser = parse_args("Generate Bedrock Titan embeddings for chunk JSON.")
    parser.add_argument("chunks_json", help="Path to data/chunks/<document_id>.json or the filename.")
    args = parser.parse_args()

    settings = load_settings()
    ensure_dirs()

    chunks_path = Path(args.chunks_json)
    if not chunks_path.is_absolute() and chunks_path.parent == Path("."):
        chunks_path = CHUNKS_DIR / chunks_path
    chunks = read_json(chunks_path)
    bedrock_runtime = boto3_client(settings, "bedrock-runtime", max_attempts=1)

    embedded = []
    for index, chunk in enumerate(chunks, start=1):
        chunk["embedding"] = bedrock_embed_text(
            bedrock_runtime,
            settings["bedrock_embedding_model_id"],
            chunk["text"],
        )
        embedded.append(chunk)
        print(f"Embedded {index}/{len(chunks)}: {chunk['chunk_id']}")

    document_id = chunks[0]["document_id"] if chunks else "empty"
    output_path = EMBEDDED_CHUNKS_DIR / f"{document_id}.json"
    write_json(output_path, embedded)
    print(f"Saved embedded chunks: {output_path}")


if __name__ == "__main__":
    main()
