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
    endpoint_configuration = [
              {
                "types": [
                  "REGIONAL"
                ],
                "vpc_endpoint_ids": []
              }]
    id = "ddmmlg41i3"
}