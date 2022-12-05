import json
import urllib3
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
        logger.info("Enviando mensagem usando bot: {} para chat: {}, método: {}, complemento: {}".format(botName, chatId, methodName, textMessage))

        botToken = get_token(botName)
        
        botUrl = 'https://api.telegram.org/bot{}/{}'.format(botToken, methodName)
        http = urllib3.PoolManager()
        options = {
            'chat_id' : chatId,
            'text' : textMessage
        }
        logger.info("Parâmetros do request. Url {}, Options: {}".format(botUrl, options))
        
        r = http.request(
            method='POST',
            url=botUrl,
            fields=options
        )

        response = json.loads(r.data.decode('utf-8'))

        logger.info("Resposta do telegram: {}".format(response))
    return response