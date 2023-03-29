locals {
  region = "us-east-1"
  subscribers_table_name = "topic_subscribers"
  telegram_api_name = "telegram"
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region  = local.region
}

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

data "archive_file" "lambdaTelegramHandler" {
  type = "zip"

  source_dir  = "${path.module}/lambdas/telegram/telegram-handler"
  output_path = "${path.module}/lambdas/zip-file/telegram-handler.zip"
}

data "archive_file" "lambdaSendMessage" {
  type = "zip"

  source_dir = "${path.module}/lambdas/telegram/send-message"
  output_path = "${path.module}/lambdas/zip-file/send-message.zip"
}

resource "aws_s3_bucket" "lambdaBucket" {
  bucket = "telegram-lambda-bucket"
}

resource "aws_s3_bucket_acl" "bucketACL" {
  bucket = aws_s3_bucket.lambdaBucket.id
  acl    = "private"
}

resource "aws_s3_object" "lambdaTelegramHandler" {
  bucket = aws_s3_bucket.lambdaBucket.id

  key    = "telegram-handler.zip"
  source = data.archive_file.lambdaTelegramHandler.output_path

  etag = filemd5(data.archive_file.lambdaTelegramHandler.output_path)
}

resource "aws_s3_object" "lambdaSendMessage" {
  bucket = aws_s3_bucket.lambdaBucket.id

  key    = "send-message.zip"
  source = data.archive_file.lambdaSendMessage.output_path

  etag = filemd5(data.archive_file.lambdaSendMessage.output_path)
}

resource "aws_lambda_function" "telegramHandler" {
  function_name = "telegram-handler"

  s3_bucket = aws_s3_bucket.lambdaBucket.id
  s3_key = aws_s3_object.lambdaTelegramHandler.key

  runtime = "python3.9"
  handler = "lambda_function.lambda_handler"

  source_code_hash = data.archive_file.lambdaTelegramHandler.output_base64sha256

  role = aws_iam_role.telegramHandlerRole.arn
}

resource "aws_lambda_function" "sendMessage" {
  function_name = "send-message"

  s3_bucket = aws_s3_bucket.lambdaBucket.id
  s3_key = aws_s3_object.lambdaSendMessage.key

  runtime = "python3.9"
  handler = "lambda_function.lambda_handler"

  source_code_hash = data.archive_file.lambdaSendMessage.output_base64sha256

  role = aws_iam_role.sendMessageRole.arn
}

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

resource "aws_apigatewayv2_api" "telegram" {
  name          = "telegram"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "devStage" {
  api_id = aws_apigatewayv2_api.telegram.id

  name        = "dev"
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "telegramHandler" {
  api_id = aws_apigatewayv2_api.telegram.id

  integration_uri    = aws_lambda_function.telegramHandler.invoke_arn
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "telegram" {
  api_id = aws_apigatewayv2_api.telegram.id

  route_key = "POST /update"
  target    = "integrations/${aws_apigatewayv2_integration.telegramHandler.id}"
}

resource "aws_cloudwatch_log_group" "apiGw" {
  name = "/aws/api_gw/${aws_apigatewayv2_api.telegram.name}"

  retention_in_days = 30
}

resource "aws_lambda_permission" "apiGw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.telegramHandler.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.telegram.execution_arn}/*/*"
}
