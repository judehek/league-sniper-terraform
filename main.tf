provider "aws" {
  region = var.region
}

data "archive_file" "build_code" {
  type = "zip"
  source_dir = "${path.module}/sniper/src"
  output_path = "${path.module}/sniper/output/python.zip"
}

resource "aws_iam_role" "lambda_role" {
  name = "lambda_role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_lambda_function" "sniper_function" {
  count = "3"
  role = aws_iam_role.lambda_role.arn
  filename = "${path.module}/sniper/output/python.zip"
  function_name = "na-sniper-${count.index + 1}"
  handler = "name_sniper.lambda_handler"
  runtime = "python3.9"
  timeout = "900"
  layers = ["arn:aws:lambda:us-east-2:260495632885:layer:leagueSniperLayer:3"]
}
