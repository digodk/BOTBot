import re
import logging
import boto3
import botocore
import os
import json
from boto3.dynamodb.conditions import Key

# Set up logger and DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('topic_subscribers')

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def valid_topic(topic):
    """
    Validate the topic to ensure it only contains alphanumeric 
    characters or underscores and is not longer than 32 characters.

    Args:
    topic (str): The topic to validate

    Returns:
    bool: True if the topic is valid, False otherwise.
    """

    return re.match(r'^[a-z0-9_]{1,32}$', topic)


def add_subscriber(topic, chat_id):
    """
    Adds a chat id subscription to a topic in the DynamoDB subscriptions table.

    Args:
    topic (str): The topic to subscribe to
    chat_id (str): The chat id to add to the subscription

    Returns:
        A json response from the call made to AWS using boto3
    """

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


def subscribe_to_topic(topic, chat_id):
    """
    Subscribes a user to a topic.

    Args:
    topic (str): The topic to subscribe to
    chat_id (str): The chat id to add to the subscription

    Returns:
    The telegram reponse to be sent to the user
    """

    topic = topic.lstrip().lower()
    if valid_topic(topic):
        add_subscriber(str(topic), str(chat_id))
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
    """
    Unsubscribe a user from a topic.

    Args:
    topic (str): The topic to unsubscribe from
    chat_id (str): The chat id to remove from the subscription
    remove_subscriber (func): A function to remove the subscriber

    Returns:
    str: A message indicating the result of the unsubscription attempt
    """

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
    """
    Publish a message to the SQS queue for sending a message to a Telegram user.

    Args:
    chatId (str): The id of the chat to send the message to
    message (str): The message to send
    botName (str, optional): The name of the bot to send the message. Defaults to 'configurator'.

    Returns:
    dict: The response from the SQS send_message function
    """

    logger.info(
        f'Publicando na fila de envio do telegram a mensagem {message} para chatId {chatId}')
    payload = {
        'botName': botName,
        'textMessage': message
    }
    return send_sqs_message([chatId], payload, 'send-message-queue')


def broadcast_message(chatId, payload, topic):
    """
    Broadcast a message to all subscribers of a topic.

    Args:
    chatId (str): The id of the chat that the message originates from
    payload (dict): The message to send
    topic (str): The topic to send the message to

    Returns:
    dict: The response from the SQS send_message function
    """

    logger.info(
        f'Divulgando mensagem {payload} para o tópico {topic}, vinda do chat {chatId}')

    subscribers = get_subscribers(topic)
    if len(subscribers) == 0:
        return

    payload = {
        'textMessage': f'.{topic}: {payload["text"]}',
        'botName': 'configurator'
    }

    response = send_sqs_message(subscribers, payload, 'send-message-queue')
    return response


def get_subscribers(topic):
    """
    Get a list of subscribers for a topic.

    Args:
    topic (str): The topic to get subscribers for

    Returns:
    list: A list of subscribers
    """

    logger.info(
        f'enviando request para os subscribers do seguinte tópico: {topic}')
    try:
        response = table.query(
            KeyConditionExpression=Key('topic').eq(topic)
        )
    except botocore.exceptions.ClientError as e:
        logger.error(e.response['Error']['Message'])
        return []
    else:
        logger.info(f'resposta obtida: {response}')
        subscribers = [item['subscriber_id'] for item in response['Items']]
        return subscribers


def send_sqs_message(recipients, payload, sqsName):
    """
    Send a message to an SQS queue.

    Args:
    recipients (list): The recipients of the message
    payload (dict): The message to send
    sqsName (str): The name of the SQS queue to send the message to

    Returns:
    dict: The response from the SQS send_message function
    """

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
