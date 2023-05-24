resource "aws_dynamodb_table" "topicSubscribers" {
  name = local.subscribers_table_name
  hash_key = "topic"
  range_key = "subscriber_id"
  billing_mode = "PAY_PER_REQUEST"

  attribute {
    name = "topic"
    type = "S"
  }

    attribute {
    name = "subscriber_id"
    type = "S"
  }

  tags = {
    Name = local.subscribers_table_name
  }
}