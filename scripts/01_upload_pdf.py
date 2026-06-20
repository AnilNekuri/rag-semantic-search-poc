from pathlib import Path

from common import boto3_client, document_id_from_path, load_settings, parse_args


def main() -> None:
    parser = parse_args("Upload a local PDF to the POC S3 input prefix.")
    parser.add_argument("pdf_path", help="Path to a local synthetic/sample PDF.")
    parser.add_argument("--s3-key", help="Optional full S3 object key.")
    args = parser.parse_args()

    settings = load_settings()
    pdf_path = Path(args.pdf_path).resolve()
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Input file must be a PDF.")

    document_id = document_id_from_path(pdf_path)
    s3_key = args.s3_key or f"{settings['s3_input_prefix']}/{document_id}.pdf"

    s3 = boto3_client(settings, "s3")
    s3.upload_file(
        str(pdf_path),
        settings["s3_bucket_name"],
        s3_key,
        ExtraArgs={"ContentType": "application/pdf"},
    )

    print(f"Uploaded {pdf_path.name}")
    print(f"s3://{settings['s3_bucket_name']}/{s3_key}")


if __name__ == "__main__":
    main()
