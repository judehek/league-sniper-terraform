provider "aws" {
  region = var.region
}

module "account_generator" {
  source = "./account_generator"
}

module "doordash_account_generator_scheduler" {
  source = "./scheduler_lambda"
  scheduler_name = "doordash_account_generator_scheduler"
  command = "aws ecs run-task --task doordashbot"
  rate_expression = "rate(7 days)"
  AWS_ACCESS_KEY_ID = var.AWS_ACCESS_KEY_ID
  AWS_SECRET_ACCESS_KEY = var.AWS_SECRET_ACCESS_KEY
}