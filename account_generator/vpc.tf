resource "aws_default_subnet" "default_aws_subnet" {
  availability_zone = "us-east-2a"

  tags = {
    Name = "Default subnet for us-east-2"
  }
}