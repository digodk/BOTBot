resource "aws_apigatewayv2_api" "telegram" {
  name          = "telegram"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "dev" {
  api_id = aws_apigatewayv2_api.telegram.id

  name        = "dev"
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "telegramHandler" {
  api_id = aws_apigatewayv2_api.telegram.id

  integration_uri    = aws_lambda_function.telegramHandler.invoke_arn
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "telegram" {
  api_id = aws_apigatewayv2_api.telegram.id

  route_key = "POST /update"
  target    = "integrations/${aws_apigatewayv2_integration.telegramHandler.id}"
}

resource "aws_cloudwatch_log_group" "apiGw" {
  name = "/aws/api_gw/${aws_apigatewayv2_api.telegram.name}"

  retention_in_days = 30
}

resource "aws_lambda_permission" "apiGw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.telegramHandler.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.telegram.execution_arn}/*/*"
}