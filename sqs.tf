# Defines the primary SQS queue for sending messages.
# Messages that cannot be processed are moved to the Dead Letter Queue after 4 attempts.
resource "aws_sqs_queue" "sendMessage" {
  name                      = "send-message-queue"
  delay_seconds             = 90     # Delays message delivery for 90 seconds
  max_message_size          = 2048   # Maximum message size is 2048 bytes
  message_retention_seconds = 86400  # Messages are retained for 86400 seconds (1 day)
  receive_wait_time_seconds = 10     # Long polling wait time is 10 seconds

  # Redrive policy defines the Dead Letter Queue and the maximum receive count.
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.sendMessageDeadletter.arn
    maxReceiveCount     = 4
  })

  # Policy that allows the AWS account to perform all SQS actions on this queue.
  policy = <<POLICY
  {
    "Version": "2008-10-17",
    "Id": "__default_policy_ID",
    "Statement": [
      {
        "Sid": "__owner_statement",
        "Effect": "Allow",
        "Principal": {
          "AWS": "arn:aws:iam::020664526196:root"
        },
        "Action": "SQS:*",
        "Resource": "arn:aws:sqs:sa-east-1:020664526196:telegram-updates"
      }
    ]
  }
  POLICY
}

# Dead Letter Queue (DLQ) associated with the primary sendMessage.
# Messages that cannot be processed after multiple attempts in the primary queue are sent here.
resource "aws_sqs_queue" "sendMessageDeadletter" {
  name = "send-message-queue-DLQ"
  message_retention_seconds = 86400  # Messages are retained for 86400 seconds (1 day)
}

# Allows the sendMessage Lambda function to be triggered by messages arriving in the sendMessage.
# The Lambda function processes messages in batches of 10.
resource "aws_lambda_event_source_mapping" "sendMessage" {
  event_source_arn = aws_sqs_queue.sendMessage.arn
  function_name = aws_lambda_function.sendMessage.arn
  batch_size = 10
}
