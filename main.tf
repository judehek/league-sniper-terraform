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
    name = "password"
    type = "S"
  }
  attribute {
    name = "date_created"
    type = "S"
  }
}