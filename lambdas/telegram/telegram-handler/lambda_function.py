# Import necessary modules
import json
import re
import logging
import boto3
from helpers import subscribe_to_topic, unsubscribe_from_topic, broadcast_message, send_telegram_message

# Define Regex patterns
SUBSCRIBE_PATTERN = re.compile(r'^/sub ?\n?(.+)')
UNSUBSCRIBE_PATTERN = re.compile(r'^/unsub ?\n?(.+)')
BROADCAST_PATTERN = re.compile(r'^\.([a-z0-9_]{1,32})[ \n]+((?!\s+$).+)')

# Setup DynamoDB resource and table fot boto3
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('topic_subscribers')

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, ctx):
    """
    Lambda function handler for processing incoming events from Telegram.

    Args:
        event (dict): The incoming event data from Telegram. This includes the body of the message.
        ctx (context): AWS Lambda Context object.

    Returns:
        dict: A response dictionary with a status code.
    """
    # Default Response
    response = {
        'statusCode': 200
    }

    # Logging received event
    logger.info(f'Recebendo evento do telegram com o payload {event}')

    # Default Telegram response
    telegram_response = "Não entendi seu comando!"

    # Parse the event body
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

    # Extract text and chat ID from the message
    text = message['text']
    chat_id = message['chat']['id']
    logger.info(f'Identificado os parâmetros: text:{text}, chatId:{chat_id}')

    # Handle commands starting with '/'
    if text.startswith('/'):
        telegram_response = handle_commands(text, chat_id)

    # Handle broadcasts, which start with '.'
    elif text.startswith('.'):
        telegram_response = handle_broadcast(text, chat_id)

    # Send the response to user in Telegram
    if telegram_response:
        send_telegram_message(chat_id, telegram_response, 'configurator')

    return response


def handle_commands(text, chat_id):
    """
    Handles the commands provided in the text from a Telegram message.

    Args:
        text (str): The text of the Telegram message.
        chat_id (int): The unique identifier for the chat where the message originated.

    Returns:
        str: The bot's response to the command.
    """

    # Handle '/start' command
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

    # Check for '/sub' command and subscribe to the topic
    topic_match = re.match(SUBSCRIBE_PATTERN, text)
    if topic_match:
        return subscribe_to_topic(topic_match.group(1), chat_id)

    # Check for '/unsub' command and unsubscribe from the topic
    topic_match = re.match(UNSUBSCRIBE_PATTERN, text)
    if topic_match:
        return unsubscribe_from_topic(topic_match.group(1), chat_id)

    return "Não entendi seu comando!"


def handle_broadcast(text, chat_id):
    """
    Handles the broadcasting of a message to a specific topic.

    Args:
        text (str): The text of the Telegram message.
        chat_id (int): The unique identifier for the chat where the message originated.

    Returns:
        str: The bot's response to the broadcast command.
    """

    # Check if the message matches the broadcast pattern
    match = re.match(BROADCAST_PATTERN, text)
    if match:
        # Extract the topic and message from the match and broadcasts the message
        topic, topic_message = match.groups()
        logger.info(
            f'Transmitindo mensagem {topic_message} para tópico {topic}')
        broadcast_message(chat_id, {'text': topic_message.strip()}, topic)
        return 'Ok! Mensagem enviada'
