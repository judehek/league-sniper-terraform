provider "aws" {
  region = var.region
}

module "account_generator" {
  source = "./account_generator"
}

module "doordash_account_generator_scheduler" {
  source = "./scheduler_lambda"
  scheduler_name = "doordash_account_generator_scheduler"
  rate_expression = "rate(7 days)"
  cluster = module.account_generator.ecs_cluster
  subnet_id = module.account_generator.ecs_subnet_id
  task_definition = module.account_generator.ecs_task_definition
}