output "ecs_cluster" {
  value = aws_ecs_cluster.doordash_account_generator_ecs_cluster.name
}

output "ecs_subnet_id" {
  value = aws_default_subnet.default_aws_subnet.id
}

output "ecs_task_definition" {
  value = aws_ecs_task_definition.doordash_account_generator_ecs_task_definition.family
}