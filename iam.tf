resource "aws_iam_role" "sendMessageRole" {
  name = "send-message-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Sid    = ""
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      }
    ]
  })
  managed_policy_arns = [
    "arn:aws:iam::020664526196:policy/SQSPolicyForLambdaExecution",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole"
  ]
}

resource "aws_iam_role" "telegramHandlerRole" {
  name = "telegram-handler-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Sid    = ""
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      }
    ]
  })
  description = "Allows Lambda functions to post logs do cloud watch as well as read and delete sqs messages"
  force_detach_policies = false
  managed_policy_arns = [
    "arn:aws:iam::020664526196:policy/DynamoDBBasicReadWriteAccess",
    "arn:aws:iam::020664526196:policy/LambdaPolicyForLambdaExecution",
    "arn:aws:iam::020664526196:policy/SNSPolicyForLambdaExecution",
    "arn:aws:iam::020664526196:policy/SQSPolicyForLambdaExecution",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole"
  ]
  max_session_duration = 3600
}