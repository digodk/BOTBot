import json
import requests
import logging
from awsHelper import get_token

def lambda_handler(event, ctx):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info("recebido evento para evnio de mensagem com o payload {}".format(event))
    records=event['Records']
    for record in records:
        body = json.loads(record['body'])
        botName = body['botName']
        textMessage = body['textMessage']
        chatId = body['chatId']
        methodName = 'sendMessage'

        botToken = get_token(botName)
        
        botUrl = 'https://api.telegram.org/bot{}/{}'.format(botToken, methodName)
        options = {
            'chat_id' : chatId,
            'text' : textMessage
        }
        
        response = requests.post(
            url=botUrl,
            json=json.dumps(options)
            ).json

    return response