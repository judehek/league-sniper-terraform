variable "region" {
  description = "AWS region"
  default = "us-east-2"
}

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