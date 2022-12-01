import json
import logging
from layers.python.awsHelper import publish_sns_topic

def lambda_handler(event, ctx):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info("recebido evento para broadcast com o payload {}".format(event))
    records=event['Records']

    for record in records:
        body = json.loads(record['body'])
        topic = body['Subject']
        userMessage = body['Message']
        sqsArn = record['eventSourceARN']
        chatId = sqsArn.split(':')[-1]
        telegramMessage = "-{} /n /n {}".format(topic, userMessage)
        logging.info("publicando evento na sns send-message, para chat id {}, com payload {}".format(chatId, telegramMessage))
        publish_sns_topic(chatId, telegramMessage)
