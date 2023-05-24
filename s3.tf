# Creates a ZIP archive of the Telegram handler lambda function code.
data "archive_file" "lambdaTelegramHandler" {
  type = "zip"

  # The source directory contains the lambda function code.
  source_dir  = "${path.module}/lambdas/telegram/telegram-handler"

  # The output path is where the ZIP file will be stored.
  output_path = "${path.module}/lambdas/zip-file/telegram-handler.zip"
}

# Creates a ZIP archive of the Send Message lambda function code.
data "archive_file" "lambdaSendMessage" {
  type = "zip"

  # The source directory contains the lambda function code.
  source_dir = "${path.module}/lambdas/telegram/send-message"

  # The output path is where the ZIP file will be stored.
  output_path = "${path.module}/lambdas/zip-file/send-message.zip"
}

# Creates an S3 bucket to store the lambda function ZIP files.
resource "aws_s3_bucket" "lambdaBucket" {
  bucket = "telegram-lambda-bucket"
}

# Sets the access control list (ACL) of the S3 bucket to private.
# This means that the bucket and its contents can only be accessed by authorized AWS users.
resource "aws_s3_bucket_acl" "bucketACL" {
  bucket = aws_s3_bucket.lambdaBucket.id
  acl    = "private"
}

# Uploads the Telegram handler lambda function ZIP file to the S3 bucket.
resource "aws_s3_object" "lambdaTelegramHandler" {
  bucket = aws_s3_bucket.lambdaBucket.id

  key    = "telegram-handler.zip"  # The key is the filename in the S3 bucket.
  source = data.archive_file.lambdaTelegramHandler.output_path

  # ETag is the MD5 hash of the file. This is used to detect changes in the file.
  etag = filemd5(data.archive_file.lambdaTelegramHandler.output_path)
}

# Uploads the Send Message lambda function ZIP file to the S3 bucket.
resource "aws_s3_object" "lambdaSendMessage" {
  bucket = aws_s3_bucket.lambdaBucket.id

  key    = "send-message.zip"  # The key is the filename in the S3 bucket.
  source = data.archive_file.lambdaSendMessage.output_path 

  # ETag is the MD5 hash of the file. This is used to detect changes in the file.
  etag = filemd5(data.archive_file.lambdaSendMessage.output_path)
}
