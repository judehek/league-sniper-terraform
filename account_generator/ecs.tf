resource "aws_cloudwatch_log_group" "doordash_account_generator_log_group" {
  name = "doordash_account_generator_log_group"
}

resource "aws_iam_role" "doordash_account_generator_role" {
  name               = "doordash_account_generator_role"
  assume_role_policy = jsonencode({
    Version   = "2022-02-06"
    Statement = [
      {
        Action = "dynamodb:*"
        Effect = "Allow"
        Principal: {
          Service: "ec2.amazonaws.com"
        },
      },
    ]
  })
}

resource "aws_ecs_task_definition" "doordash_account_generator_ecs_task_definition" {
  container_definitions    = var.doordash_account_generator_ecs_definition
  family                   = "doordash-account-generator"
  requires_compatibilities = [
    "FARGATE"
  ]
  network_mode             = "awsvpc"
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = var.ecsTaskExecutionRole
  task_role_arn            = aws_iam_role.doordash_account_generator_role.arn
  lifecycle {
    ignore_changes = [
      container_definitions]
  }
}

resource "aws_ecs_cluster" "doordash_account_generator_ecs_cluster" {
  name               = "doordash_account_generator_ecs_cluster"
  capacity_providers = [
    "FARGATE"
  ]
  default_capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 1
    base              = 1
  }
}

resource "aws_ecs_service" "doordash_account_generator_ecs" {
  name            = "doordash_account_generator_ecs"
  cluster         = aws_ecs_cluster.doordash_account_generator_ecs_cluster.id
  task_definition = aws_ecs_task_definition.doordash_account_generator_ecs_task_definition.arn
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = [
      aws_default_subnet.default_aws_subnet.id
    ]
    assign_public_ip = true
  }
}
