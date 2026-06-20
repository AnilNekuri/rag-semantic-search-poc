from pathlib import Path

from opensearchpy import helpers

from common import EMBEDDED_CHUNKS_DIR, load_settings, opensearch_client, parse_args, read_json


def main() -> None:
    parser = parse_args("Bulk index embedded chunks into OpenSearch Serverless.")
    parser.add_argument("embedded_chunks_json", help="Path to data/embedded-chunks/<document_id>.json or the filename.")
    args = parser.parse_args()

    settings = load_settings()
    chunks_path = Path(args.embedded_chunks_json)
    if not chunks_path.is_absolute() and chunks_path.parent == Path("."):
        chunks_path = EMBEDDED_CHUNKS_DIR / chunks_path
    chunks = read_json(chunks_path)
    client = opensearch_client(settings)

    actions = [
        {
            "_op_type": "index",
            "_index": settings["opensearch_index_name"],
            "_source": chunk,
        }
        for chunk in chunks
    ]

    success, errors = helpers.bulk(client, actions, raise_on_error=False)
    print(f"Indexed {success} chunks into {settings['opensearch_index_name']}.")
    if errors:
        raise RuntimeError(f"OpenSearch indexing returned {len(errors)} errors. First error: {errors[0]}")


if __name__ == "__main__":
    main()
