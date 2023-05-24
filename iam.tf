# IAM role for the Send Message lambda function.
resource "aws_iam_role" "sendMessageRole" {
  name = "send-message-role"

  # The assume_role_policy is the policy that grants an entity permission to assume the role.
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Sid    = ""
      Principal = {
        Service = "lambda.amazonaws.com"  # The entity that is allowed to assume the role is the Lambda service.
      }
      }
    ]
  })

  # Managed policies that are attached to the role. These policies grant the role permissions to perform specific actions.
  managed_policy_arns = [
    "arn:aws:iam::020664526196:policy/SQSPolicyForLambdaExecution",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole"
  ]
}

# IAM role for the Telegram Handler lambda function.
resource "aws_iam_role" "telegramHandlerRole" {
  name = "telegram-handler-role"

  # The assume_role_policy is the policy that grants an entity permission to assume the role.
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Sid    = ""
      Principal = {
        Service = "lambda.amazonaws.com"  # The entity that is allowed to assume the role is the Lambda service.
      }
      }
    ]
  })

  # A description of the role.
  description = "Allows Lambda functions to post logs do cloud watch as well as read and delete sqs messages"

  # Whether policies can be detached from the role when it is deleted. If false, the role can be deleted without removing the policies.
  force_detach_policies = false

  # The managed policies that are attached to the role. These policies grant the role permissions to perform specific actions.
  managed_policy_arns = [
    "arn:aws:iam::020664526196:policy/DynamoDBBasicReadWriteAccess",
    "arn:aws:iam::020664526196:policy/LambdaPolicyForLambdaExecution",
    "arn:aws:iam::020664526196:policy/SNSPolicyForLambdaExecution",
    "arn:aws:iam::020664526196:policy/SQSPolicyForLambdaExecution",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole"
  ]

  # The maximum duration of a session that uses the role, in seconds.
  max_session_duration = 3600
}
