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
    if not 'message' in update:
        return response

    message = update['message']

    # TODO Allow to broadcast media other than text
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
    # TODO Include command to check subscriptions
    # Handle '/start' command
    if text == '/start':
        return (introduction_message())

    # Check for '/sub' command and subscribe to the topic
    topic_match = re.match(SUBSCRIBE_PATTERN, text)
    if topic_match:
        return subscribe_to_topic(topic_match.group(1), chat_id)

    # Check for '/unsub' command and unsubscribe from the topic
    topic_match = re.match(UNSUBSCRIBE_PATTERN, text)
    if topic_match:
        return unsubscribe_from_topic(topic_match.group(1), chat_id)

    # Check for '/about' command and return the bot's description and a link to the project
    if text == '/about':
        return about_message()

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


def introduction_message():
    bot_intro = "Olá, eu sou o BOTBot! (Broadcast Over Topics Bot)"
    bot_function = "Eu faço transmissão de mensagens. Você pode tentar os seguintes comandos comigo:"
    subscribe_info = "/sub nome_do_topico para você se inscrever em um tópico. Tópicos podem ter caracteres alfanuméricos e o símbolo _"
    unsubscribe_info = "/unsub nome_topico para você se desinscrever de um tópico."
    message_info = ".nome_do_topico sua mensagem de texto para enviar uma mensagem para um tópico. Todas as pessoas inscritas vão receber uma cópia da mensagem."
    about_info = "/about para saber mais sobre o BOTBot"

    return f"""
    {bot_intro}
        
    {bot_function}

    {subscribe_info}

    {unsubscribe_info}

    {message_info}

    {about_info}
    """

def about_message():
    """
    Returns the bot's description and a link to the project.
    """

    return f"""
    Olá, eu sou o BOTBot! (Broadcast Over Topics Bot)
    Este é um projeto de aprendizagem sobre aplicações serverless, ferramentas de cloud e DevOps.
    O BOTBot é um bot do Telegram projetado para facilitar a inscrição em tópicos e a publicação anônima de mensagens.
    Os usuários podem se inscrever ou cancelar a inscrição em tópicos, e postar mensagens de texto nesses tópicos.
        
    Este projeto usa vários scripts Python e arquivos Terraform para gerenciar os recursos AWS necessários para o bot.
        
    Para mais informações, acesse o link do projeto: https://github.com/digodk/BOTBot
    """
