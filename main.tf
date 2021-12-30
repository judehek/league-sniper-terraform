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
  rate_expression = "rate(2 minutes)"
}