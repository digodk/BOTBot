from moto import mock_sns, mock_sqs, mock_lambda
from lambda_function import lambda_handler
import boto3

@mock_sns
@mock_sqs
@mock_lambda
def test_topic_subscription():
    event = {
        "Records":[
            {
                "body":'{"update_id":510534520,\n"message":{"message_id":203,"from":{"id":54337384,"is_bot":false,"first_name":"Diogo","username":"digodk","language_code":"pt-br"},"chat":{"id":54337384,"first_name":"Diogo","username":"digodk","type":"private"},"date":1670874229,"text":"/sub qualquercoisa","entities":[{"offset":0,"length":4,"type":"bot_command"}]}}'
            }
        ]
    }
    ctx = {}
    response = lambda_handler(event, ctx)
    print(response)
    return True