import json
import re
import logging
import boto3
import botocore
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('topic_subscribers')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

response = {
    'stausCode': 200
}


def lambda_handler(event, ctx):
    logger.info('Recebendo evento do telegram com o payload {}'.format(event))
    records = event['Records']
    for record in records:
        telegramResponse = "Não entendi seu comando!"
        update = json.loads(record['body'])

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
                if re.match(r'^[a-z0-9_]+$', topic):
                    add_subscriber(topic, chatId)
                    telegramResponse = f'Ok! Você foi inscrito no tópico {topic}. Quando você receber uma mensagem nesse tópico, ela vai vir assim: \n' + \
                        f'.{topic}\nmensagem recebida'
                else:
                    logger.info('nome inválido de tópico')
                    telegramResponse = 'Tópico inválido! Tópicos devem ter apenas caracteres alfanuméricos ou _'

            # Unsubscribe from topic
            if re.match(r'^/unsub ?\n?', text):
                topic = re.sub(r'^/unsub ?\n?', '', text, 0).lstrip().lower()
                logger.info(
                    f'Solicitada a desinscrição do chat {chatId} do tópico {topic}')
                if re.match(r'^[a-z0-9_]+$', topic):
                    remove_subscriber(topic, chatId)
                    telegramResponse = 'Ok! Sua inscrição do tópico {} foi removida'.format(
                        topic)
                else:
                    telegramResponse = 'Tópico inválido! Tópicos devem ter apenas caracteres alfanuméricos ou _'

        if text[0] == '.':
            # Broadcast a message
            match = re.search(r'^\.[a-z0-9_]+[ \n]+', text)
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
                telegramResponse = 'Tópico inválido! Tópicos devem ter apenas caracteres alfanuméricos ou _'
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
        print(e.response['Error']['Message'])
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
    logger.info('Divulgando mensagem {} para o tópico {}, vinda do chat {}'.format(
        message, topic, chatId))
    payload = {
        'topic': topic,
        'user_message': message,
        'chat_id': chatId
    }
    response = publish_sns_topic(chatId, payload, "broadcast")
    return response


def publish_sns_topic(chatId, payload, snsName="send-telegram-response"):
    sns = boto3.client('sns')

    awsReg = os.environ.get('AWS_REGION')

    awsAccount = os.environ.get('AWS_ACCOUNT_ID')

    logger.info('Publicando mensagem: {} no sns: {}'.format(payload, snsName))

    payload['chatId'] = chatId

    jhon = json.dumps(payload)

    logger.info('Publicando Json : {} no sns: {}'.format(jhon, snsName))

    arnSNS = 'arn:aws:sns:{}:{}:{}'.format(
        awsReg, awsAccount, snsName)

    logger.info("Assim ficou a string do arnSNS: {}".format(arnSNS))

    response = sns.publish(TopicArn=arnSNS, Message=jhon)
    logger.info("Essa foi a resposta da AWS {}".format(response))
    return response


def send_telegram_message(chatId, message, botName='configurator'):
    logger.info('Publicando na fila de envio do telegram a mensagem {} para chatId {}'.format(
        message, chatId))
    payload = {
        'botName': botName,
        'textMessage': message
    }
    response = send_sqs_message(chatId, payload, 'outgoing-messages')
    return response


def send_sqs_message(chatId, payload, sqsName, topic=''):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    awsAccount = os.environ.get('AWS_ACCOUNT_ID')

    sqs = boto3.client('sqs')
    sqsUrl = sqs.get_queue_url(
        QueueName=sqsName,
        QueueOwnerAWSAccountId=awsAccount
    )['QueueUrl']

    payload['chatId'] = chatId
    if topic != '':
        payload['topic'] = topic

    jhon = json.dumps(payload)

    logger.info(
        'enviando para a fila: {} /n no url {} /n payload: {}'.format(sqsName, sqsUrl, jhon))

    response = sqs.send_message(
        QueueUrl=sqsUrl,
        MessageBody=jhon)
    return response
