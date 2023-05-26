terraform {
  backend "remote" {
    organization = "digodk-tutorial"

    workspaces {
      name = "bot-bot"
    }
  }
}
