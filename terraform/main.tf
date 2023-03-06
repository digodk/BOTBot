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

resource "aws_api_gateway_rest_api" "telegramWebhook" {
    name = local.telegram_api_name
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

resource "aws_dynamodb_table" "topic_subscribers" {
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


