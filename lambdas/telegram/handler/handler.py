import json
import re

from layers.python.awsHelper import (broadcast_message, send_telegram_message,
                                     subscribe_chat_to_topic)


def lambda_handler(event, ctx):
    #TODO
    update = json.loads(event[0])
    telMessage = update['Message']
    text = telMessage['text']
    chatId = update['chat_id']
    if text[0] == '.':
        #Comando para inscrever usuário
        if re.match(r'^/subs ?\n?', text):
            topic = re.sub(r'^/subs ?\n?','', text, 0).lstrip().lower
            if re.match(r'^[a-z0-9_]$'):
                subscribe_chat_to_topic(topic, chatId)
                response = 'Ok! Você foi inscrito no tópico .{}'.format(topic)
            else:
                response = 'Tópicos devem ter apenas caracteres alfanuméricos ou _'
    
    if text[0] == '.':
        topic = re.search(r'^\.[a-z0-9_]+[ \n]+', text)
        if topic:
            topicMessage = re.sub(r'^\.[a-z0-9_]+[ \n]+', '', text)
            if not topicMessage == '':
                payload = {
                    'text':topicMessage.strip()
                }
                broadcast_message(chatId, payload, topic.strip())
                response = 'Ok! Mensagem enviada!'

    if response: send_telegram_message(chatId, response)