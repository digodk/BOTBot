import json
import urllib3
import logging
import os


def lambda_handler(event, ctx):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info(
        f'recebido evento para evnio de mensagem com o payload {event}')
    records = event['Records']
    for record in records:
        body = json.loads(record['body'])
        botName = body['botName']
        textMessage = body['textMessage']
        recipients = body['recipients']
        for chatId in recipients:
            methodName = 'sendMessage'
            logger.info(
                f'Enviando mensagem usando bot: {botName} para chat: {chatId}, método: {methodName}, complemento: {textMessage}')

            botToken = get_token(botName)

            botUrl = f'https://api.telegram.org/bot{botToken}/{methodName}'
            http = urllib3.PoolManager()
            options = {
                'chat_id': chatId,
                'text': textMessage
            }
            logger.info(
                f'Parâmetros do request. Url {botUrl}, Options: {options}')

            r = http.request(
                method='POST',
                url=botUrl,
                fields=options
            )

            response = json.loads(r.data.decode('utf-8'))
            logger.info(f'Resposta do telegram: {response}')
    return


def get_token(botName):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if botName == 'broadcaster':
        botToken = broadcaster_token()
    if botName == 'configurator':
        botToken = configurator_token()
    logger.info(f'Obtido o token {botToken} para o bot {botName}')
    return botToken


def configurator_token():
    token = os.environ.get('CONFIGURATOR_TELEGRAM_TOKEN')
    return token


def broadcaster_token():
    token = os.environ.get('BROADCASTER_TELEGRAM_TOKEN')
    return token
