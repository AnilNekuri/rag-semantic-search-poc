output "project_name" {
  description = "Project name used for tags and resource naming."
  value       = var.project_name
}

output "aws_region" {
  description = "AWS region configured for this POC."
  value       = var.aws_region
}

output "aws_profile" {
  description = "AWS CLI profile configured for local Terraform runs."
  value       = var.aws_profile
}

output "opensearch_index_name" {
  description = "OpenSearch index name that will be created by the Python index setup script."
  value       = var.opensearch_index_name
}

output "opensearch_collection_name" {
  description = "OpenSearch Serverless vector collection name."
  value       = aws_opensearchserverless_collection.vector.name
}

output "opensearch_collection_arn" {
  description = "OpenSearch Serverless vector collection ARN."
  value       = aws_opensearchserverless_collection.vector.arn
}

output "opensearch_collection_endpoint" {
  description = "OpenSearch Serverless collection endpoint for the Python scripts."
  value       = aws_opensearchserverless_collection.vector.collection_endpoint
}

output "opensearch_dashboard_endpoint" {
  description = "OpenSearch Serverless dashboard endpoint."
  value       = aws_opensearchserverless_collection.vector.dashboard_endpoint
}

output "bedrock_embedding_model_id" {
  description = "Bedrock embedding model ID used by the POC scripts."
  value       = var.bedrock_embedding_model_id
}

output "bedrock_region" {
  description = "AWS region used by local scripts for Bedrock embedding calls."
  value       = var.bedrock_region
}

output "s3_bucket_name" {
  description = "S3 bucket for source PDF uploads."
  value       = aws_s3_bucket.documents.bucket
}

output "s3_input_prefix" {
  description = "Recommended S3 prefix for uploaded PDF input files."
  value       = "input/"
}

output "local_script_iam_policy_arn" {
  description = "IAM policy ARN with permissions for local POC scripts."
  value       = aws_iam_policy.local_script_permissions.arn
}

output "env_file_values" {
  description = "Suggested values to copy into the local .env file."
  value = {
    AWS_REGION                     = var.aws_region
    BEDROCK_REGION                 = var.bedrock_region
    S3_BUCKET_NAME                 = aws_s3_bucket.documents.bucket
    S3_INPUT_PREFIX                = "input/"
    BEDROCK_EMBEDDING_MODEL_ID     = var.bedrock_embedding_model_id
    OPENSEARCH_COLLECTION_ENDPOINT = aws_opensearchserverless_collection.vector.collection_endpoint
    OPENSEARCH_INDEX_NAME          = var.opensearch_index_name
  }
}

output "env_file_text" {
  description = "Copy-paste friendly .env content for local Python scripts."
  value       = <<EOT
AWS_REGION=${var.aws_region}
AWS_PROFILE=${var.aws_profile}
BEDROCK_REGION=${var.bedrock_region}
S3_BUCKET_NAME=${aws_s3_bucket.documents.bucket}
S3_INPUT_PREFIX=input/
BEDROCK_EMBEDDING_MODEL_ID=${var.bedrock_embedding_model_id}
OPENSEARCH_COLLECTION_ENDPOINT=${aws_opensearchserverless_collection.vector.collection_endpoint}
OPENSEARCH_INDEX_NAME=${var.opensearch_index_name}
EOT
}
