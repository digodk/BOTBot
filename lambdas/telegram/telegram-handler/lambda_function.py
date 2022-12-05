import json
import re
import logging
from awsHelper import (broadcast_message, send_telegram_message,
                                      subscribe_chat_to_topic, unsubscribe_chat_from_topic)

response={
    'stausCode':200
}
def lambda_handler(event, ctx):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info("Recebendo evento do telegram com o payload {}".format(event))
    records=event['Records']
    for record in records:
        update = json.loads(record['body'])
        message = update['message']
        text = message['text']
        chatId = message['chat']['id']
        logger.info("Identificado os parâmetros: text:{}, chatId:{}".format(text, chatId))
        if text[0] == '/':
            telegramResponse = "Não entendi seu comando!"
            #Comando para inscrever usuário
            if re.match(r'^/subs ?\n?', text):
                topic = re.sub(r'^/subs ?\n?','', text, 0).lstrip().lower()
                logger.info("Identificado o comando para inscrever no tópico {}".format(topic))
                if re.match(r'^[a-z0-9_]+$', topic):
                    subscribe_chat_to_topic(topic, chatId)
                    telegramResponse = 'Ok! Você foi inscrito no tópico {}'.format(topic)
                else:
                    logger.info('nome inválido de tópico')
                    telegramResponse = 'Tópico inválido! Tópicos devem ter apenas caracteres alfanuméricos ou _'

            #Comando para desinscrever-se
            if  re.match(r'^/unsub ?\n?', text):
                topic = re.sub(r'^/unsub ?\n?','', text, 0).lstrip().lower
                if re.match(r'^[a-z0-9_]$', topic): 
                    unsubscribe_chat_from_topic(topic, chatId)
                    telegramResponse = 'Ok! Sua inscrição do tópico {} foi removida'.format(topic)
                else:
                    telegramResponse = 'Tópico inválido! Tópicos devem ter apenas caracteres alfanuméricos ou _'

        if text[0] == '.':
            #Comando para transmitir uma mensagem
            topic = re.search(r'^\.[a-z0-9_]+[ \n]+', text)
            if topic:
                topicMessage = re.sub(r'^\.[a-z0-9_]+[ \n]+', '', text)
                if not topicMessage == '':
                    payload = {
                        'text':topicMessage.strip()
                    }
                    broadcast_message(chatId, payload, topic.strip())
                    telegramResponse = 'Ok! Mensagem enviada!'
                else:
                    telegramResponse = 'Não consegui entender sua mensgem!'
            else:
                telegramResponse = 'Tópico inválido! Tópicos devem ter apenas caracteres alfanuméricos ou _'
        if telegramResponse: 
            send_telegram_message(chatId, telegramResponse, 'configurator')
    return response