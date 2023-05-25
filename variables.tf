
variable "configurator_bot_token" {
  description = "Telegram token for the configurator bot. Provided by terraform cloud"
}

locals {
  region = "us-east-1"
  subscribers_table_name = "topic_subscribers"
  telegram_api_name = "telegram"
  aws_account_id = "020664526196"
}