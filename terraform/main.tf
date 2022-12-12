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
  region  = "sa-east-1"
}

resource "aws_api_gateway_rest_api" "telegram-webhook" {
    name = "telegram"
}

resource "aws_api_gateway_resource" "config-bot" {
    rest_api_id = aws_api_gateway_rest_api.telegram-webhook.id
    parent_id = aws_api_gateway_rest_api.telegram-webhook.root_resource_id
    path_part = "config-bot"
}

resource "aws_api_gateway_method" "config-bot-post" {
  rest_api_id = aws_api_gateway_rest_api.telegram-webhook.id
  resource_id = aws_api_gateway_resource.config-bot.id
  http_method = "POST"
  authorization = "NONE"
}

resource "aws_iam_role" "apiLambdaIntegrationRole" {
  
}

resource "aws_api_gateway_integration" "config-bot-post-integration" {
  rest_api_id = aws_api_gateway_rest_api.telegram-webhook.id
  resource_id = aws_api_gateway_resource.config-bot.id
  http_method = aws_api_gateway_method.config-bot-post.http_method
  type = "AWS"
  integration_http_method = "POST"
  credentials = "arn:aws:iam::020664526196:role/AWSRoleForAPIGateway"
  request_parameters = {
              "integration.request.header.Content-Type": "'application/x-www-form-urlencoded'"
            }
  request_templates = {
              "application/json": "Action=SendMessage\u0026MessageBody=$input.body"
            }
  uri = "arn:aws:apigateway:sa-east-1:sqs:path/020664526196/telegram-updates"
}

