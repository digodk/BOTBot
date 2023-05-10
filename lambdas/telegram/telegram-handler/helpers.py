import re
import logging
import boto3
import botocore
import os
import json
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO)
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('topic_subscribers')

def valid_topic(topic):
    return re.match(r'^[a-z0-9_]{1,32}$', topic)


def subscribe_to_topic(topic, chat_id, add_subscriber):
    topic = topic.lstrip().lower()
    if valid_topic(topic):
        add_subscriber(topic, chat_id)
        return (
            f'Ok! Você foi inscrito no tópico {topic}. '
            f'Quando você receber uma mensagem nesse tópico, ela vai vir assim:\n'
            f'.{topic}\nmensagem recebida'
        )
    else:
        return (
            'Tópico inválido! Tópicos devem ter apenas caracteres alfanuméricos '
            'ou _ e no máximo 32 caracteres'
        )


def unsubscribe_from_topic(topic, chat_id, remove_subscriber):
    topic = topic.lstrip().lower()
    if valid_topic(topic):
        remove_subscriber(topic, chat_id)
        return f'Ok! Sua inscrição do tópico {topic} foi removida'
    else:
        return (
            'Tópico inválido! Tópicos devem ter apenas caracteres alfanuméricos '
            'ou _ e no máximo 32 caracteres'
        )


def send_telegram_message(chatId, message, botName='configurator'):

    logger.info(
        f'Publicando na fila de envio do telegram a mensagem {message} para chatId {chatId}')
    payload = {
        'botName': botName,
        'textMessage': message
    }
    response = send_sqs_message([chatId], payload, 'send-message-queue')
    return response


def broadcast_message(chatId, message, topic):
    logger.info(
        f'Divulgando mensagem {message} para o tópico {topic}, vinda do chat {chatId}')

    subscribers = get_subscribers(topic)
    if len(subscribers) == 0:
        return

    payload = {
        'textMessage': f'.{topic}: {message}',
        'botName': 'configurator'
    }

    response = send_sqs_message(subscribers, payload, 'send-message-queue')
    return response


def get_subscribers(topic):
    try:
        response = table.query(
            KeyConditionExpression=Key('topic').eq(topic)
        )
    except botocore.exceptions.ClientError as e:
        logger.error(e.response['Error']['Message'])
        return []
    else:
        subscribers = [item['subscriber_id'] for item in response['Items']]
        return subscribers


def send_sqs_message(recipients, payload, sqsName):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    awsAccount = os.environ.get('AWS_ACCOUNT_ID')

    sqs = boto3.client('sqs')
    sqsUrl = sqs.get_queue_url(
        QueueName=sqsName,
        QueueOwnerAWSAccountId=awsAccount
    )['QueueUrl']

    payload['recipients'] = recipients

    jsonPayload = json.dumps(payload)

    logger.info(
        f'enviando para a fila: {sqsName} /n no url {sqsUrl} /n payload: {jsonPayload}')

    response = sqs.send_message(
        QueueUrl=sqsUrl,
        MessageBody=jsonPayload)

    logger.info(f'Resposta recebida: {response}')
    return response
