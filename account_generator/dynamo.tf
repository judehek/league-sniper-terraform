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
    name = "is_original"
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
    name            = "IsOriginalIndex"
    hash_key        = "is_original"
    projection_type = "ALL"
  }
  global_secondary_index {
    name            = "IsUsedIndex"
    hash_key        = "is_used"
    projection_type = "ALL"
  }
}

resource "aws_dynamodb_table" "original_tracking" {
  hash_key     = "email"
  name         = "original_tracking"
  billing_mode = "PAY_PER_REQUEST"
  attribute {
    name = "email"
    type = "S"
  }
}