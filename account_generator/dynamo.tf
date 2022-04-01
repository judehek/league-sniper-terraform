resource "aws_dynamodb_table" "doordash_accounts" {
  hash_key     = "email"
  name         = "doordash_accounts"
  billing_mode = "PAY_PER_REQUEST"
  attribute {
    name = "email"
    type = "S"
  }
  attribute {
    name = "date_created"
    type = "S"
  }
  attribute {
    name = "is_used"
    type = "S"
  }
  global_secondary_index {
    name            = "DateCreatedIndex"
    hash_key        = "date_created"
    projection_type = "ALL"
  }
  global_secondary_index {
    name            = "IsUsedIndex"
    hash_key        = "is_used"
    projection_type = "ALL"
  }
}

resource "aws_dynamodb_table" "account_counting" {
  hash_key     = "email"
  name         = "account_counting"
  billing_mode = "PAY_PER_REQUEST"
  attribute {
    name = "email"
    type = "S"
  }
}