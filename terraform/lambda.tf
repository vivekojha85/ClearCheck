resource "aws_lambda_function" "sam_gov_pull" {
  filename         = "../src/lambda/sam_gov_pull.zip"
  function_name    = "sam-gov-pull"
  role            = aws_iam_role.lambda_role.arn
  handler         = "main.handler"
  runtime         = "python3.9"
  timeout         = 60
  memory_size     = 256

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.source.id
    }
  }

  vpc_config {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }

  tags = {
    Environment = var.environment
  }
}
