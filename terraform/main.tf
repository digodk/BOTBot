local "region" {
  default = "sa-east-1"
}

local "subscribers_table_name"{
  default = "topic_subscribers"
}

local "telegram_api_name"{
  default = "telegram"
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
  region  = var.region
}

resource "aws_api_gateway_rest_api" "telegramWebhook" {
    name = var.telegram_api_name
}

resource "aws_api_gateway_resource" "configBot" {
    rest_api_id = aws_api_gateway_rest_api.telegramWebhook.id
    parent_id = aws_api_gateway_rest_api.telegramWebhook.root_resource_id
    path_part = "config-bot"
}

resource "aws_api_gateway_method" "configBotPost" {
  rest_api_id = aws_api_gateway_rest_api.telegramWebhook.id
  resource_id = aws_api_gateway_resource.configBot.id
  http_method = "POST"
  authorization = "NONE"
}

resource "aws_iam_role" "apiLambdaIntegrationRole" {
  assume_role_policy = "{\"Statement\":[{\"Action\":\"sts:AssumeRole\",\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"apigateway.amazonaws.com\"},\"Sid\":\"\"}],\"Version\":\"2012-10-17\"}"
  description = "Allows API Gateway to push logs to CloudWatch Logs and send messages do telegram-updates queue"
  name = "AWSRoleForAPIGateway"
  managed_policy_arns = [
    "arn:aws:iam::020664526196:policy/SQSTelegram-UpdatesSendMessagePolicy",
    "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
  ]
}

resource "aws_api_gateway_integration" "configBotPostIntegration" {
  rest_api_id = aws_api_gateway_rest_api.telegramWebhook.id
  resource_id = aws_api_gateway_resource.configBot.id
  http_method = aws_api_gateway_method.configBotPost.http_method
  type = "AWS"
  integration_http_method = "POST"
  credentials = aws_iam_role.apiLambdaIntegrationRole.arn
  request_parameters = {
              "integration.request.header.Content-Type": "'application/x-www-form-urlencoded'"
            }
  request_templates = {
              "application/json": "Action=SendMessage\u0026MessageBody=$input.body"
            }
  uri = "arn:aws:apigateway:sa-east-1:sqs:path/020664526196/telegram-updates"
}

resource "aws_dynamodb_table" "topic_subscribers" {
  name = var.subscribers_table_name
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
    Name = var.subscribers_table_name
  }
}


