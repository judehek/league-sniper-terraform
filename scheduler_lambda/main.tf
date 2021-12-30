


module "lambda_function" {
  source = "registry.terraform.io/terraform-aws-modules/lambda/aws"

  function_name = var.scheduler_name
  description   = "Lambda function to invoke a command"
  handler       = "scheduler_lambda.handler"
  runtime       = "nodejs14.x"
  publish       = true
  source_path   = "./src/lambda/built/scheduler_lambda.js"
  allowed_triggers = {
    All = {
      principal = "events.amazon.com"
      source_arn = module.eventbridge.eventbridge_rule_arns[0]
    }
  }
}

module "eventbridge" {
  source = "registry.terraform.io/terraform-aws-modules/eventbridge/aws"

  create_bus = false

  rules = {
    crons = {
      description         = "Trigger for a Lambda"
      schedule_expression = var.rate_expression
    }
  }

  targets = {
    crons = [
      {
        name  = "lambda-cron"
        arn   = module.lambda_function.lambda_function_arn
        input = jsonencode({
          "job": "cron-by-rate"
        })
      }
    ]
  }
}