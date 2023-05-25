variable "config_bot_token" {
  description = "Token for the configurator bot"
}

locals {
  region = "us-east-1"
  subscribers_table_name = "topic_subscribers"
  telegram_api_name = "telegram"
  aws_account_id = "020664526196"
  configurator_bot_token = var.config_bot_token
}