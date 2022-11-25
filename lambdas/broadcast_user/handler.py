import json
import logging
from layers.python.awsHelper import publish_sns_topic

def lambda_handler(event, ctx):
    sqs_payload = json.loads(event['Records'])
    
    logging.info("recebido evento para broadcast com o payload {}".format(sqs_payload))

    for record in sqs_payload:
        snsMessage = record['body']
        topic = snsMessage['Subject']
        userMessage = snsMessage['Message']
        sqsArn = record['eventSourceARN']
        chatId = sqsArn.split(':')[-1]
        telegramMessage = "-{} /n /n {}".format(topic, userMessage)
        logging.info("publicando evento na sns send-message, para chat id {}, com payload {}".format(chatId, telegramMessage))
        publish_sns_topic(chatId, telegramMessage)
