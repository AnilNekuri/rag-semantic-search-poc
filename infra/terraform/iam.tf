locals {
  poc_policy_name = "${var.opensearch_collection_name}-local-script-policy"
}

data "aws_iam_policy_document" "local_script_permissions" {
  statement {
    sid = "S3DocumentBucketAccess"

    actions = [
      "s3:GetBucketLocation",
      "s3:ListBucket"
    ]

    resources = [
      aws_s3_bucket.documents.arn
    ]
  }

  statement {
    sid = "S3DocumentObjectAccess"

    actions = [
      "s3:DeleteObject",
      "s3:GetObject",
      "s3:PutObject"
    ]

    resources = [
      "${aws_s3_bucket.documents.arn}/*"
    ]
  }

  statement {
    sid = "TextractAsyncTextDetection"

    actions = [
      "textract:GetDocumentTextDetection",
      "textract:StartDocumentTextDetection"
    ]

    resources = ["*"]
  }

  statement {
    sid = "BedrockEmbeddingInvoke"

    actions = [
      "bedrock:InvokeModel"
    ]

    resources = [
      "arn:aws:bedrock:${var.bedrock_region}::foundation-model/${var.bedrock_embedding_model_id}"
    ]
  }

  statement {
    sid = "OpenSearchServerlessApiAccess"

    actions = [
      "aoss:APIAccessAll",
      "aoss:BatchGetCollection",
      "aoss:ListCollections"
    ]

    resources = [
      aws_opensearchserverless_collection.vector.arn
    ]
  }

  statement {
    sid = "OpenSearchServerlessListCollections"

    actions = [
      "aoss:ListCollections"
    ]

    resources = ["*"]
  }
}

resource "aws_iam_policy" "local_script_permissions" {
  name        = local.poc_policy_name
  description = "Permissions for local scripts in the AWS RAG semantic search POC."
  policy      = data.aws_iam_policy_document.local_script_permissions.json

  tags = {
    Name = local.poc_policy_name
  }
}

resource "aws_iam_role_policy_attachment" "local_script_permissions" {
  for_each = toset(var.poc_iam_role_names_to_attach)

  role       = each.value
  policy_arn = aws_iam_policy.local_script_permissions.arn
}
