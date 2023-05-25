resource "aws_lambda_function" "telegramHandler" {
  function_name = "telegram-handler"

  s3_bucket = aws_s3_bucket.lambda.id
  s3_key = aws_s3_object.lambdaTelegramHandler.key

  runtime = "python3.9"
  handler = "lambda_function.lambda_handler"

  source_code_hash = data.archive_file.lambdaTelegramHandler.output_base64sha256

  role = aws_iam_role.telegramHandler.arn

  environment {
    variables = {
      AWS_ACCOUNT_ID = local.aws_account_id
    }
  }
}

resource "aws_lambda_function" "sendMessage" {
  function_name = "send-message"

  s3_bucket = aws_s3_bucket.lambda.id
  s3_key = aws_s3_object.lambdaSendMessage.key

  runtime = "python3.9"
  handler = "lambda_function.lambda_handler"

  source_code_hash = data.archive_file.lambdaSendMessage.output_base64sha256

  role = aws_iam_role.sendMessage.arn

  environment {
    variables = {
      AWS_ACCOUNT_ID = local.aws_account_id
      CONFIGURATOR_TELEGRAM_TOKEN = var.configurator_bot_token
    }
  }
}