provider "aws" {
  region = var.region
}

resource "aws_dynamodb_table" "doordash_accounts" {
  hash_key = "email"
  name = "doordash_accounts"
  billing_mode = "PAY_PER_REQUEST"
  attribute {
    name = "email"
    type = "S"
  }
  attribute {
    name = "date_created"
    type = "S"
  }
  global_secondary_index {
    name = "DateCreatedIndex"
    hash_key = "date_created"
    projection_type = "ALL"
  }
}

resource "aws_ecr_repository" "doordash_account_creator" {
  name = "doordash_account_creator"
}

resource "aws_ecr_lifecycle_policy" "doordash_account_creator_registry_lifecycle_policy" {
  policy = var.doordash_ecr_lifecycle_policy
  repository = aws_ecr_repository.doordash_account_creator.id
}

