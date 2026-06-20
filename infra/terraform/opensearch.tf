locals {
  opensearch_policy_name_prefix = substr(var.opensearch_collection_name, 0, 24)
}

resource "aws_opensearchserverless_security_policy" "encryption" {
  name = "${local.opensearch_policy_name_prefix}-enc"
  type = "encryption"

  policy = jsonencode({
    Rules = [
      {
        ResourceType = "collection"
        Resource = [
          "collection/${var.opensearch_collection_name}"
        ]
      }
    ]
    AWSOwnedKey = true
  })
}

resource "aws_opensearchserverless_security_policy" "network" {
  name = "${local.opensearch_policy_name_prefix}-net"
  type = "network"

  policy = jsonencode([
    {
      Rules = [
        {
          ResourceType = "collection"
          Resource = [
            "collection/${var.opensearch_collection_name}"
          ]
        },
        {
          ResourceType = "dashboard"
          Resource = [
            "collection/${var.opensearch_collection_name}"
          ]
        }
      ]
      AllowFromPublic = true
    }
  ])
}

resource "aws_opensearchserverless_collection" "vector" {
  name             = var.opensearch_collection_name
  type             = "VECTORSEARCH"
  standby_replicas = "DISABLED"

  depends_on = [
    aws_opensearchserverless_security_policy.encryption
  ]

  tags = {
    Name = var.opensearch_collection_name
  }
}

resource "aws_opensearchserverless_access_policy" "data_access" {
  count = length(var.aoss_data_access_principal_arns) > 0 ? 1 : 0

  name = "${local.opensearch_policy_name_prefix}-data"
  type = "data"

  policy = jsonencode([
    {
      Rules = [
        {
          ResourceType = "collection"
          Resource = [
            "collection/${var.opensearch_collection_name}"
          ]
          Permission = [
            "aoss:CreateCollectionItems",
            "aoss:DeleteCollectionItems",
            "aoss:UpdateCollectionItems",
            "aoss:DescribeCollectionItems"
          ]
        },
        {
          ResourceType = "index"
          Resource = [
            "index/${var.opensearch_collection_name}/*"
          ]
          Permission = [
            "aoss:CreateIndex",
            "aoss:DeleteIndex",
            "aoss:UpdateIndex",
            "aoss:DescribeIndex",
            "aoss:ReadDocument",
            "aoss:WriteDocument"
          ]
        }
      ]
      Principal = var.aoss_data_access_principal_arns
    }
  ])
}
