resource "aws_sqs_queue" "sendMessageQueue" {
  name                      = "send-message-queue"
  delay_seconds             = 90
  max_message_size          = 2048
  message_retention_seconds = 86400
  receive_wait_time_seconds = 10
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.sendMessageQueueDeadletter.arn
    maxReceiveCount     = 4
  })
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

resource "aws_sqs_queue" "sendMessageQueueDeadletter" {
  name = "send-message-queue-DLQ"
  message_retention_seconds = 86400
}

resource "aws_lambda_event_source_mapping" "sendMessageQueue" {
  event_source_arn = aws_sqs_queue.sendMessageQueue.arn
  function_name = aws_lambda_function.sendMessage.arn
  batch_size = 10
}