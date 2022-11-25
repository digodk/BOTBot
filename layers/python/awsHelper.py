import json
import logging

import boto3

OK_RESPONSE = {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': json.dumps('ok')
}

ERROR_RESPONSE = {
    'statusCode': 400,
    'body': json.dumps('Oops, something went wrong!')
}

def get_token(botName):
    if botName == 'broadcaster':
        botToken = broadcaster_token
    if botName == 'configurator':
        botToken = configurator_token

def configurator_token():
    with open('environment.json', 'r') as arquivo:
        data = arquivo.read()

    jhon = json.loads(data)
    token = jhon['CONFIGURATOR_TELEGRAM_TOKEN']
    return token

def broadcaster_token():
    with open('environment.json', 'r') as arquivo:
        data = arquivo.read()

    jhon = json.loads(data)
    token = jhon['BROADCASTER_TELEGRAM_TOKEN']
    return token

def subscribe_chat_to_topic(topic, chatId):
    client = boto3.client('sns')
    topicArn = create_topic_sns(topic)
    queueArn = create_chat_sqs(chatId)
    response = client.subscribe(
        TopicArn=topicArn,
        Protocol='sqs',
        Endpoint=queueArn
    )
    return response['SubscriptionArn']

def unsubscribe_chat_from_topic(topic, chat_id):
    #TODO
    return True

def create_topic_sns(topic):
    client = boto3.client('sns')
    response = client.create_topic(
        Name=topic
    )
    return response['TopicArn']

def create_chat_sqs(chat_id):
    sqsClient = boto3.client('sqs')
    lambdaClient = boto3.client('lambda')

    # Confere se já existe uma fila co chat antes de tentar criar uma
    try:
        sqsResponse = sqsClient.get_queue_url(
            QueueName=chat_id
        )
    except:
        queueExists = False
        sqsResponse = sqsClient.create_queue(
            QueueName=chat_id
        )
    else:
        queueExists = True

    # Obtém ARN a partir da URL
    queueUrl = sqsResponse['QueueUrl']
    queueAttributes = sqsClient.get_queue_attributes(
        QueueUrl=queueUrl,
        AttributeNames=[
            'QueueArn'
        ]
    )
    queueArn = queueAttributes['Attributes']['QueueArn']

    # Se a fila não existe, então também é necessário mapear ela como trigger da lambda
    if not queueExists:
        lambdaClient.create_event_source_mapping(
            EventSourceArn=queueArn,
            FunctionName='broadcast_user'
        )
    return queueArn

def send_telegram_message(chatId, message):
    #TODO
    payload = {}
    publish_sns_topic(chatId, payload)
    return True

def broadcast_message(chatId, message, topic):
    #TODO se tópico não existe, criar ele
    payload = {
        'user_message':mssage,
        'chat_id':chatId
    }
    response = publish_sns_topic(chatId, payload, topic, topic)
    return response

def publish_sns_topic(chatId, payload, snsName="send-telegram-response", subject=""):

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    sns = boto3.client('sns')  # criamos um SNS para enviar

    my_session = boto3.session.Session()
    aws_reg = my_session.region_name  # nome da região

    with open('environment.json', 'r') as arquivo:
        data = arquivo.read()

    jhon = json.loads(data)

    aws_account = jhon['AWS_ACCOUNT_ID']
    tenant = jhon['TENANT']

    logger.info(aws_reg)
    logger.info(aws_account)

    # aqui é o log do que vamos mandar e para onde
    logger.info('Publicando mensagem: {} no sns: {}'.format(payload, snsName))

    # vamos formatar o json de saida

    PyJson = json.loads(payload)

    PyJson['chatId'] = chatId

    jhon = json.dumps(PyJson)

    logger.info('Publicando Json : {} no sns: {}'.format(jhon, snsName))

    # ajeitamos o sns nome correto
    arnSNS = 'arn:aws:sns:{}:{}:{}-{}'.format(
        aws_reg, aws_account, tenant, snsName)

    logger.info("Assim ficou a string do arnSNS: {}".format(arnSNS))
    # aqui envia a resposta
    response = sns.publish(TopicArn=arnSNS, Message=jhon, Subject=subject)
    return response