module "lambda_function" {
  source = "registry.terraform.io/terraform-aws-modules/lambda/aws"

  function_name          = var.scheduler_name
  description            = "Lambda function to invoke a command"
  handler                = "LambdaHandler"
  runtime                = "java11"
  publish                = true
  create_package         = false
  local_existing_package = "./lambdas/target/SchedulerLambda-1.0.jar"
  timeout                = 60
  memory_size            = 512

  attach_policy_jsons  = true
  policy_jsons     = [
    <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecs:RunTask"
            ],
            "Resource": ["*"]
        }
    ]
}
EOF
,
<<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iam:PassRole"
            ],
            "Resource": ["*"]
        }
    ]
}
EOF
  ]
  number_of_policy_jsons = 2

  allowed_triggers = {
    All = {
      principal  = "events.amazonaws.com"
      source_arn = module.eventbridge.eventbridge_rule_arns["crons"]
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
        name  = var.scheduler_name
        arn   = module.lambda_function.lambda_function_arn
        input = jsonencode({
          "cluster": var.cluster,
          "subnet": var.subnet_id
          "taskDefinition": var.task_definition
        })
      }
    ]
  }
}