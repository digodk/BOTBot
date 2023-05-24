# Due to an update to Terraform Cloud in 2022, Terraform variables without default values in the configuration
# for workspaces that use the VCS workflow are automatically detected and assigned an empty value of type `HCL`.
# This can lead to validation errors when the variable is used. To prevent this, a `default` value of `null` is set. 
# This ensures that if the `configurator_bot_token` is not provided, its value will be `null` and not an empty HCL value.
# This variable is actually provided by Github secrets.
variable "configurator_bot_token" {
  description = "The token for the configurator bot"
  type = string
  default = null
}

locals {
  region = "us-east-1"
  subscribers_table_name = "topic_subscribers"
  telegram_api_name = "telegram"
  aws_account_id = "020664526196"
  configurator_bot_token = var.configurator_bot_token
}