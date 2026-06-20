import time
from collections import defaultdict
from pathlib import Path

from common import EXTRACTED_TEXT_DIR, boto3_client, ensure_dirs, load_settings, parse_args, write_json


def collect_blocks(textract, job_id: str) -> list[dict]:
    blocks = []
    next_token = None

    while True:
        kwargs = {"JobId": job_id}
        if next_token:
            kwargs["NextToken"] = next_token
        response = textract.get_document_text_detection(**kwargs)
        blocks.extend(response.get("Blocks", []))
        next_token = response.get("NextToken")
        if not next_token:
            return blocks


def main() -> None:
    parser = parse_args("Run Textract async text extraction for a PDF in S3.")
    parser.add_argument("s3_key", help="S3 key of the uploaded PDF, for example input/sample.pdf.")
    parser.add_argument("--document-id", help="Optional document ID. Defaults to PDF filename stem.")
    parser.add_argument("--poll-seconds", type=int, default=5, help="Polling interval in seconds.")
    args = parser.parse_args()

    settings = load_settings()
    ensure_dirs()

    document_id = args.document_id or Path(args.s3_key).stem.replace(" ", "_")
    textract = boto3_client(settings, "textract")

    start = textract.start_document_text_detection(
        DocumentLocation={
            "S3Object": {
                "Bucket": settings["s3_bucket_name"],
                "Name": args.s3_key,
            }
        }
    )
    job_id = start["JobId"]
    print(f"Started Textract job: {job_id}")

    while True:
        status_response = textract.get_document_text_detection(JobId=job_id, MaxResults=1)
        status = status_response["JobStatus"]
        print(f"Textract status: {status}")

        if status == "SUCCEEDED":
            break
        if status in {"FAILED", "PARTIAL_SUCCESS"}:
            message = status_response.get("StatusMessage", "No status message returned.")
            raise RuntimeError(f"Textract job ended with {status}: {message}")
        time.sleep(args.poll_seconds)

    lines_by_page: dict[int, list[str]] = defaultdict(list)
    for block in collect_blocks(textract, job_id):
        if block.get("BlockType") == "LINE":
            lines_by_page[int(block.get("Page", 1))].append(block.get("Text", ""))

    output = {
        "document_id": document_id,
        "s3_bucket": settings["s3_bucket_name"],
        "s3_key": args.s3_key,
        "textract_job_id": job_id,
        "pages": [
            {"page_number": page_number, "text": "\n".join(lines)}
            for page_number, lines in sorted(lines_by_page.items())
        ],
    }

    output_path = EXTRACTED_TEXT_DIR / f"{document_id}.json"
    write_json(output_path, output)
    print(f"Saved extracted text: {output_path}")


if __name__ == "__main__":
    main()
