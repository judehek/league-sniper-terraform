provider "aws" {
  region = var.region
}

module "account_generator" {
  source = "./account_generator"
}

moved {
  from = aws_cloudwatch_log_group.doordash_account_generator_log_group
  to = module.account_generator.aws_cloudwatch_log_group.doordash_account_generator_log_group
}