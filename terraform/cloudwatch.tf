resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/sam-gov-pull"
  retention_in_days = 14

  tags = {
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "glue_logs" {
  name              = "/aws/glue/load-data"
  retention_in_days = 14

  tags = {
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "opensearch_logs" {
  name              = "/aws/opensearch/mf-codeblooded"
  retention_in_days = 14

  tags = {
    Environment = var.environment
  }
}
