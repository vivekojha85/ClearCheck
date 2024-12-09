resource "aws_dynamodb_table" "sam_gov" {
  name           = "sam_gov_exclusions_v2"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5
  
  hash_key = "id"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "entity_type"
    type = "S"
  }

  attribute {
    name = "agency"
    type = "S"
  }

  attribute {
    name = "active_date"
    type = "S"
  }

  global_secondary_index {
    name               = "entity_type-index"
    hash_key           = "entity_type"
    range_key         = "id"
    write_capacity     = 5
    read_capacity      = 5
    projection_type    = "ALL"
  }

  global_secondary_index {
    name               = "agency-active-index"
    hash_key           = "agency"
    range_key         = "active_date"
    write_capacity     = 5
    read_capacity      = 5
    projection_type    = "ALL"
  }

  point_in_time_recovery {
    enabled = true
  }

  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  tags = {
    Environment = var.environment
  }
}