import json
import re
import logging
import boto3
import botocore
import os
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('topic_subscribers')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, ctx):
    response = {
        'stausCode': 200
    }

    logger.info('Recebendo evento do telegram com o payload {}'.format(event))
    telegramResponse = "Não entendi seu comando!"
    update = json.loads(event['body'])

    # If the update is about an edited message exit the function, discarding the update
    if 'edited_message' in update:
        return

    # WIP Temporary code that discards any update which is not a text message
    # TODO Allow to broadcast media other than text
    # TODO Include command to check subscriptions
    if not 'message' in update:
        return response

    message = update['message']

    if not 'text' in message:
        return response

    text = message['text']
    chatId = message['chat']['id']
    logger.info(
        "Identificado os parâmetros: text:{}, chatId:{}".format(text, chatId))
    if text.startswith('/'):
        if text == '/start':
            telegramResponse = "Olá, eu sou o BOTBot! (Broadcast Over Topics Bot) \n" + \
                "Eu faço transmissão de mensagens. Você pode tentar os seguintes comandos comigo: \n\n" + \
                "/sub nome_do_topico\npara você se inscrever em um tópico. Tópicos podem ter caracteres alfanuméricos e o símbolo _ \n\n" + \
                "/unsub nome_topico\npara você se desinscrever de um tópico.\n\n" + \
                ".nome_do_topico sua mensagem de texto\npara enviar uma mensagem para um tópico. Todas as pessoas inscritas vão receber uma cópia da mensagem. \n\n"

        # Subscribe to topic
        if re.match(r'^/sub ?\n?', text):
            topic = re.sub(r'^/sub ?\n?', '', text, 0).lstrip().lower()
            logger.info(
                "Identificado o comando para inscrever no tópico {}".format(topic))
            if re.match(r'^[a-z0-9_]{1,32}$', topic):
                add_subscriber(topic, chatId)
                telegramResponse = f'Ok! Você foi inscrito no tópico {topic}. Quando você receber uma mensagem nesse tópico, ela vai vir assim: \n' + \
                    f'.{topic}\nmensagem recebida'
            else:
                logger.info('nome inválido de tópico')
                telegramResponse = 'Tópico inválido! Tópicos devem ter apenas caracteres alfanuméricos ou _ e no máximo 32 caracteres'

        # Unsubscribe from topic
        if re.match(r'^/unsub ?\n?', text):
            topic = re.sub(r'^/unsub ?\n?', '', text, 0).lstrip().lower()
            logger.info(
                f'Solicitada a desinscrição do chat {chatId} do tópico {topic}')
            if re.match(r'^[a-z0-9_]{1,32}$', topic):
                remove_subscriber(topic, chatId)
                telegramResponse = 'Ok! Sua inscrição do tópico {} foi removida'.format(
                    topic)
            else:
                telegramResponse = 'Tópico inválido! Tópicos devem ter apenas caracteres alfanuméricos ou _ e no máximo 32 caracteres'

    if text.startswith('.'):
        # Broadcast a message
        match = re.search(r'^\.[a-z0-9_]{1,32}[ \n]+', text)
        if match:
            topic = match.group(0).strip().lower()[1:]
            topicMessage = re.sub(r'^\.[a-z0-9_]+[ \n]+', '', text)
            if topicMessage:
                logger.info("Transmitindo mensagem {} para tópico {}".format(
                    topicMessage, topic))
                payload = {
                    'text': topicMessage.strip()
                }
                broadcast_message(chatId, payload, topic)
                telegramResponse = 'Ok! Mensagem enviada!'
            else:
                telegramResponse = 'Não consegui entender sua mensagem!'
        else:
            telegramResponse = 'Tópico inválido! Tópicos devem ter apenas caracteres alfanuméricos ou _ e no máximo 32 caracteres'
    if telegramResponse:
        send_telegram_message(chatId, telegramResponse, 'configurator')
    return response


def add_subscriber(topic, chat_id):
    try:
        response = table.get_item(
            Key={
                'topic': topic,
                'subscriber_id': chat_id
            }
        )
    except botocore.exceptions.ClientError as e:
        logger.error(e.response['Error']['Message'])
    else:
        if 'Item' not in response:
            table.put_item(
                Item={
                    'topic': topic,
                    'subscriber_id': chat_id
                }
            )
            return {
                'statusCode': 200,
                'body': json.dumps(f'Sua inscrição no tópico {topic} foi confirmada! Quando você receber uma mensagem nesse tópico, ela vai vir assim: \n' +
                                   f'.{topic}\nmensagem recebida')
            }
        else:
            return {
                'statusCode': 200,
                'body': json.dumps(f'Você já tem uma inscrição no tópico {topic}')
            }


def remove_subscriber(topic, chat_id):
    try:
        table.delete_item(
            Key={
                'topic': topic,
                'subscriber_id': chat_id
            }
        )
        return {
            'statusCode': 200,
            'body': json.dumps(f'Sua inscrição no tópico {topic} foi cancelada.')
        }
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {
                'statusCode': 404,
                'body': json.dumps(f'Não havia uma inscrição sua no tópico {topic}')
            }
        else:
            raise


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


def send_telegram_message(chatId, message, botName='configurator'):

    logger.info(
        f'Publicando na fila de envio do telegram a mensagem {message} para chatId {chatId}')
    payload = {
        'botName': botName,
        'textMessage': message
    }
    response = send_sqs_message([chatId], payload, 'send-message-queue')
    return response
