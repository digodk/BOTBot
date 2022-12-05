import json
import logging
from awsHelper import send_telegram_message

def lambda_handler(event, ctx):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info("recebido evento para broadcast com o payload {}".format(event))
    records=event['Records']

    for record in records:
        body = json.loads(record['body'])
        topic = body['Subject']
        payload = json.loads(body['Message'])
        logger.info(f"Identificado o payload {payload} do body {body}")
        userMessage = payload['user_message']
        logger.info(f"Identificado o user message {userMessage}")
        text = userMessage['text']
        sqsArn = record['eventSourceARN']
        chatId = sqsArn.split(':')[-1]
        telegramMessage = ".{} \n{}".format(topic, text)
        logging.info("publicando evento na sns send-message, para chat id {}, com payload {}".format(chatId, telegramMessage))
        send_telegram_message(chatId, telegramMessage, 'configurator')
