variable "scheduler_name" {
  type = string
}


module "lambda_function" {
  source = "registry.terraform.io/terraform-aws-modules/lambda/aws"

  function_name = var.scheduler_name
  description   = "Lambda function to invoke a command"
  handler       = "index.handler"
  runtime       = "nodejs14.x"
  publish       = true
  source_path = "./src/lambda/built/scheduler_lambda.js"
}