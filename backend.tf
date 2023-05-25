terraform {
  backend "s3" {
    bucket = "bot-bot-terraform-backend"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}