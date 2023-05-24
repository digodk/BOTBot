data "archive_file" "lambdaTelegramHandler" {
  type = "zip"

  source_dir  = "${path.module}/lambdas/telegram/telegram-handler"
  output_path = "${path.module}/lambdas/zip-file/telegram-handler.zip"
}

data "archive_file" "lambdaSendMessage" {
  type = "zip"

  source_dir = "${path.module}/lambdas/telegram/send-message"
  output_path = "${path.module}/lambdas/zip-file/send-message.zip"
}

resource "aws_s3_bucket" "lambdaBucket" {
  bucket = "telegram-lambda-bucket"
}

resource "aws_s3_bucket_acl" "bucketACL" {
  bucket = aws_s3_bucket.lambdaBucket.id
  acl    = "private"
}

resource "aws_s3_object" "lambdaTelegramHandler" {
  bucket = aws_s3_bucket.lambdaBucket.id

  key    = "telegram-handler.zip"
  source = data.archive_file.lambdaTelegramHandler.output_path

  etag = filemd5(data.archive_file.lambdaTelegramHandler.output_path)
}

resource "aws_s3_object" "lambdaSendMessage" {
  bucket = aws_s3_bucket.lambdaBucket.id

  key    = "send-message.zip"
  source = data.archive_file.lambdaSendMessage.output_path

  etag = filemd5(data.archive_file.lambdaSendMessage.output_path)
}