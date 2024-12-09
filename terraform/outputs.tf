output "website_endpoint" {
  value = aws_s3_bucket_website_configuration.website.website_endpoint
}

output "opensearch_endpoint" {
  value = aws_opensearch_domain.main.endpoint
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.sam_gov.name
}
