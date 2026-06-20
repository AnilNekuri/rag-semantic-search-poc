from pathlib import Path

from common import CHUNKS_DIR, EXTRACTED_TEXT_DIR, ensure_dirs, parse_args, read_json, write_json


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    clean_text = " ".join(text.split())
    if not clean_text:
        return []
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size.")

    chunks = []
    start = 0
    while start < len(clean_text):
        end = min(start + chunk_size, len(clean_text))
        chunks.append(clean_text[start:end])
        if end == len(clean_text):
            break
        start = end - chunk_overlap
    return chunks


def main() -> None:
    parser = parse_args("Split extracted Textract page text into overlapping chunks.")
    parser.add_argument("extracted_json", help="Path to data/extracted-text/<document_id>.json.")
    parser.add_argument("--chunk-size", type=int, default=1000)
    parser.add_argument("--chunk-overlap", type=int, default=150)
    args = parser.parse_args()

    ensure_dirs()
    extracted_path = Path(args.extracted_json)
    if not extracted_path.is_absolute() and extracted_path.parent == Path("."):
        extracted_path = EXTRACTED_TEXT_DIR / extracted_path
    extracted = read_json(extracted_path)
    document_id = extracted["document_id"]

    chunks = []
    for page in extracted["pages"]:
        page_number = page["page_number"]
        for index, text in enumerate(chunk_text(page["text"], args.chunk_size, args.chunk_overlap), start=1):
            chunks.append(
                {
                    "chunk_id": f"{document_id}_page_{page_number}_chunk_{index}",
                    "document_id": document_id,
                    "page_number": page_number,
                    "s3_key": extracted["s3_key"],
                    "text": text,
                }
            )

    output_path = CHUNKS_DIR / f"{document_id}.json"
    write_json(output_path, chunks)
    print(f"Saved {len(chunks)} chunks: {output_path}")


if __name__ == "__main__":
    main()
