resource "aws_ecr_repository" "doordash_account_creator" {
  name = "doordash_account_creator"
}

resource "aws_ecr_lifecycle_policy" "doordash_account_creator_registry_lifecycle_policy" {
  policy     = var.doordash_ecr_lifecycle_policy
  repository = aws_ecr_repository.doordash_account_creator.id
}