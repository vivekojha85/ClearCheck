resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "sam-gov-pull-lambda-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name        = "Errors"
  namespace          = "AWS/Lambda"
  period             = "300"
  statistic          = "Sum"
  threshold          = "0"
  alarm_description  = "Lambda function error rate exceeded"
  alarm_actions      = [aws_sns_topic.alerts.arn]

  dimensions = {
    FunctionName = aws_lambda_function.sam_gov_pull.function_name
  }
}

resource "aws_cloudwatch_metric_alarm" "dynamodb_read_throttle" {
  alarm_name          = "dynamodb-read-throttling"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name        = "ReadThrottleEvents"
  namespace          = "AWS/DynamoDB"
  period             = "300"
  statistic          = "Sum"
  threshold          = "0"
  alarm_description  = "DynamoDB read throttling detected"
  alarm_actions      = [aws_sns_topic.alerts.arn]

  dimensions = {
    TableName = aws_dynamodb_table.sam_gov.name
  }
}