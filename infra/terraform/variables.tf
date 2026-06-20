variable "project_name" {
  description = "Name used for tagging and naming POC resources."
  type        = string
  default     = "aws-rag-document-semantic-search-poc"
}

variable "aws_region" {
  description = "AWS region for the POC infrastructure."
  type        = string
  default     = "us-east-2"
}

variable "aws_profile" {
  description = "AWS CLI profile Terraform should use for local development."
  type        = string
  default     = "anekur-admin"
}

variable "environment" {
  description = "Environment label for tags."
  type        = string
  default     = "poc"
}

variable "bucket_name_prefix" {
  description = "Prefix for the S3 bucket that will store source PDFs."
  type        = string
  default     = "aws-rag-poc-documents"

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]{1,45}[a-z0-9]$", var.bucket_name_prefix))
    error_message = "Bucket name prefix must use lowercase letters, numbers, and hyphens only, and must start and end with a letter or number."
  }
}

variable "s3_force_destroy" {
  description = "Whether Terraform may delete the S3 bucket even when it contains objects. Enabled for this disposable POC so terraform destroy can clean up everything."
  type        = bool
  default     = true
}

variable "opensearch_collection_name" {
  description = "Name for the OpenSearch Serverless vector search collection."
  type        = string
  default     = "rag-semantic-poc"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,31}$", var.opensearch_collection_name))
    error_message = "OpenSearch Serverless collection name must be 3-32 characters, start with a lowercase letter, and contain only lowercase letters, numbers, and hyphens."
  }
}

variable "opensearch_index_name" {
  description = "Name of the vector index that the Python setup script will create."
  type        = string
  default     = "claims-rag-index"
}

variable "bedrock_embedding_model_id" {
  description = "Bedrock embedding model used by the local scripts."
  type        = string
  default     = "amazon.titan-embed-text-v2:0"
}

variable "bedrock_region" {
  description = "AWS region used by local scripts for Bedrock embedding calls. This may differ from the infrastructure region to avoid regional throttling."
  type        = string
  default     = "us-east-1"
}

variable "aoss_data_access_principal_arns" {
  description = "IAM principal ARNs that should receive OpenSearch Serverless data access in a later step."
  type        = list(string)
  default     = []
}

variable "poc_iam_role_names_to_attach" {
  description = "Optional IAM role names to attach the local script policy to. Leave empty when using an existing admin SSO profile."
  type        = list(string)
  default     = []
}
