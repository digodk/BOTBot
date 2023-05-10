import json
import re
import logging
import boto3
from helpers import subscribe_to_topic, unsubscribe_from_topic, broadcast_message, send_telegram_message

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('topic_subscribers')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, ctx):
    response = {
        'statusCode': 200
    }

    logger.info(f'Recebendo evento do telegram com o payload {event}')
    telegram_response = "Não entendi seu comando!"
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
    chat_id = message['chat']['id']
    logger.info(f'Identificado os parâmetros: text:{text}, chatId:{chat_id}')

    if text.startswith('/'):
        telegram_response = handle_commands(text, chat_id)
    elif text.startswith('.'):
        telegram_response = handle_broadcast(text, chat_id)

    if telegram_response:
        send_telegram_message(chat_id, telegram_response, 'configurator')
    return response


def handle_commands(text, chat_id):
    if text == '/start':
        return (
            "Olá, eu sou o BOTBot! (Broadcast Over Topics Bot)\n"
            "Eu faço transmissão de mensagens. Você pode tentar os seguintes comandos comigo:\n\n"
            "/sub nome_do_topico\n"
            "para você se inscrever em um tópico. Tópicos podem ter caracteres alfanuméricos e o símbolo _\n\n"
            "/unsub nome_topico\n"
            "para você se desinscrever de um tópico.\n\n"
            ".nome_do_topico sua mensagem de texto\n"
            "para enviar uma mensagem para um tópico. Todas as pessoas inscritas vão receber uma cópia da mensagem.\n\n"
        )

    # Subscribe to topic
    topic_match = re.match(r'^/sub ?\n?(.+)', text)
    if topic_match:
        return subscribe_to_topic(topic_match.group(1), chat_id)

    # Unsubscribe from topic
    topic_match = re.match(r'^/unsub ?\n?(.+)', text)
    if topic_match:
        return unsubscribe_from_topic(topic_match.group(1), chat_id)

    return "Não entendi seu comando!"


def handle_broadcast(text, chat_id):
    match = re.match(r'^\.([a-z0-9_]{1,32})[ \n]+((?!\s+$).+)', text)
    if match:
        topic, topic_message = match.groups()
        logger.info(
            f'Transmitindo mensagem {topic_message} para tópico {topic}')
        broadcast_message(chat_id, {'text': topic_message.strip()}, topic)
        return 'Ok! Mensagem enviada'



