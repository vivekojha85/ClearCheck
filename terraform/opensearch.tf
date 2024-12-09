resource "aws_opensearch_domain" "main" {
  domain_name    = "mf-codeblooded"
  engine_version = "OpenSearch_2.18"

  cluster_config {
    instance_type = "t3.medium.search"
    instance_count = 2
    zone_awareness_enabled = true
    
    zone_awareness_config {
      availability_zone_count = 2
    }
  }

  vpc_options {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.opensearch.id]
  }

  ebs_options {
    ebs_enabled = true
    volume_size = 20
    volume_type = "gp3"
  }

  encrypt_at_rest {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  tags = {
    Environment = var.environment
  }
}