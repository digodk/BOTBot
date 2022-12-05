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
        telegramResponse = "Não entendi seu comando!"
        update = json.loads(record['body'])

        #TODO - Ignorar edição de mensagens

        #WIP Código temporário que ignora qualquer update que não seja uma mensagem de texto
        if not 'message' in update:
            return response
        
        message = update['message']

        if not 'text' in message:
            return response

        text = message['text']
        chatId = message['chat']['id']
        logger.info("Identificado os parâmetros: text:{}, chatId:{}".format(text, chatId))
        if text[0] == '/':
            if text == '/start':
                telegramResponse = "Olá, eu sou o BOTBot! (Broadcast Over Topics Bot) \n" + \
                    "Eu faço transmissão de mensagens. Você pode tentar os seguintes comandos comigo: \n\n" + \
                    "/sub nome_do_topico\npara você se inscrever em um tópico. Tópicos podem ter caracteres alfanuméricos e o símbolo _ \n\n" + \
                    "/unsub nome_topico\npara você se desinscrever de um tópico.\n\n" + \
                    ".nome_do_topico sua mensagem de texto\npara enviar uma mensagem para um tópico. Todas as pessoas inscritas vão receber uma cópia da mensagem. \n\n"
            #Comando para inscrever usuário
            if re.match(r'^/sub ?\n?', text):
                topic = re.sub(r'^/sub ?\n?','', text, 0).lstrip().lower()
                logger.info("Identificado o comando para inscrever no tópico {}".format(topic))
                if re.match(r'^[a-z0-9_]+$', topic):
                    subscribe_chat_to_topic(topic, chatId)
                    telegramResponse = f'Ok! Você foi inscrito no tópico {topic}. Quando você receber uma mensagem nesse tópico, ela vai vir assim: \n' + \
                        f'.{topic}\nmensagem enviada'
                else:
                    logger.info('nome inválido de tópico')
                    telegramResponse = 'Tópico inválido! Tópicos devem ter apenas caracteres alfanuméricos ou _'

            #Comando para desinscrever-se
            if  re.match(r'^/unsub ?\n?', text):
                topic = re.sub(r'^/unsub ?\n?','', text, 0).lstrip().lower()
                logger.info(f'Solicitada a desinscrição do chat {chatId} do tópico {topic}')
                if re.match(r'^[a-z0-9_]+$', topic): 
                    unsubscribe_chat_from_topic(topic, chatId)
                    telegramResponse = 'Ok! Sua inscrição do tópico {} foi removida'.format(topic)
                else:
                    telegramResponse = 'Tópico inválido! Tópicos devem ter apenas caracteres alfanuméricos ou _'

        if text[0] == '.':
            #Comando para transmitir uma mensagem
            match = re.search(r'^\.[a-z0-9_]+[ \n]+', text)
            if match:
                topic = match.group(0).strip().lower()[1:]
                topicMessage = re.sub(r'^\.[a-z0-9_]+[ \n]+', '', text)
                if topicMessage:
                    logger.info("Transmitindo mensagem {} para tópico {}".format(topicMessage, topic))
                    payload = {
                        'text':topicMessage.strip()
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