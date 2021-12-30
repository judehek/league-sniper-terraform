variable "doordash_ecr_lifecycle_policy" {
  default = <<EOF
{
    "rules": [
        {
            "rulePriority": 1,
            "description": "Rule 1",
            "selection": {
                "tagStatus": "any",
                "countType": "imageCountMoreThan",
                "countNumber": 1
            },
            "action": {
                "type": "expire"
            }
        }
    ]
}
EOF
}

variable "doordash_account_generator_ecs_definition" {
  default = <<TASK_DEFINITION
[
  {
    "name": "doordash-account-generator-container",
    "image": "hello-world:latest",
    "cpu": 512,
    "memory": 1024,
    "essential": true,
    "logConfiguration": {
          "logDriver": "awslogs",
          "options": {
            "awslogs-group": "doordash_account_generator_log_group",
            "awslogs-region": "us-east-2",
            "awslogs-stream-prefix": "ecs"
          }
    }
  }
]
TASK_DEFINITION
}

variable "ecsTaskExecutionRole" {
  default = "arn:aws:iam::719795077267:role/ecsTaskExecutionRole"
}