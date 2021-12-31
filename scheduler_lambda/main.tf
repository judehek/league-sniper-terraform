module "lambda_function" {
  source = "registry.terraform.io/terraform-aws-modules/lambda/aws"

  function_name = var.scheduler_name
  description   = "Lambda function to invoke a command"
  handler       = "LambdaHandler"
  runtime       = "java11"
  publish       = true
  source_path   = "./lambdas/target/SchedulerLambda-1.0.jar"
  timeout = 60
  allowed_triggers = {
    All = {
      principal = "events.amazonaws.com"
      source_arn = module.eventbridge.eventbridge_rule_arns["crons"]
    }
  }
  environment_variables = {
    AWS_ACCESS_KEY_ID = var.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = var.AWS_SECRET_ACCESS_KEY
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
        name  = var.scheduler_name
        arn   = module.lambda_function.lambda_function_arn
        input = jsonencode({
          "job": "cron-by-rate"
        })
      }
    ]
  }
}