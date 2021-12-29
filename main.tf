provider "aws" {
  region = var.region
}

resource "aws_dynamodb_table" "doordash_accounts" {
  hash_key = "email"
  name = "doordash_accounts"
  billing_mode = "PAY_PER_REQUEST"
  attribute {
    name = "email"
    type = "S"
  }
  attribute {
    name = "date_created"
    type = "S"
  }
  global_secondary_index {
    name = "DateCreatedIndex"
    hash_key = "date_created"
    projection_type = "ALL"
  }
}

resource "aws_default_subnet" "default_aws_subnet" {
  availability_zone = "us-east-2a"

  tags = {
    Name = "Default subnet for us-east-2"
  }

}

resource "aws_ecr_repository" "doordash_account_creator" {
  name = "doordash_account_creator"
}

resource "aws_ecr_lifecycle_policy" "doordash_account_creator_registry_lifecycle_policy" {
  policy = var.doordash_ecr_lifecycle_policy
  repository = aws_ecr_repository.doordash_account_creator.id
}

resource "aws_ecs_task_definition" "doordash_account_generator_ecs_task_definition" {
  container_definitions = var.doordash_account_generator_ecs_definition
  family = "doordash-account-generator"
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = 512
  memory = 1024
  execution_role_arn = var.ecsTaskExecutionRole

}

resource "aws_cloudwatch_log_group" "doordash_account_generator_log_group" {
  name = "doordash_account_generator_log_group"
}

resource "aws_ecs_cluster" "doordash_account_generator_ecs_cluster" {
  name = "doordash_account_generator_ecs_cluster"
}

resource "aws_ecs_service" "doordash_account_generator_ecs" {
  name = "doordash_account_generator_ecs"
  cluster = aws_ecs_cluster.doordash_account_generator_ecs_cluster.id
  task_definition = aws_ecs_task_definition.doordash_account_generator_ecs_task_definition.arn
  launch_type = "FARGATE"
  network_configuration {
    subnets = [
      aws_default_subnet.default_aws_subnet.id
    ]
    assign_public_ip = true
  }
}
