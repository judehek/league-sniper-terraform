provider "aws" {
  region = var.region
}

module "sniper_layer" {
  source = "${path.module}/layer"
  create_layer = true
  layer_name = "sniper-layer"
  source_path = "${path.module}/layer"
}

data "archive_file" "build_code" {
  type = "zip"
  source_dir = "${path.module}/sniper/src"
  output_path = "${path.module}/sniper/output/output.zip"
}

resource "aws_lambda_function" "sniper_function" {
  count = "20"
  filename = "${path.module}/sniper/output/output.zip"
  function_name = "na-sniper-${count.index + 1}"
  runtime = "python3.9"
  timeout = "900"
  layers = [
    module.sniper_layer,
  ]
}
