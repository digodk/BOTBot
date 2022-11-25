import json
import requests
from layers.python.awsHelper import get_token

def lambda_handler(event, ctx):
    #TODO confirmar formato do objeto event
    for letter in event:
        botName = letter['botName']
        textMessage = letter['textMessage']
        chatId = letter['chatId']
        methodName = 'sendMessage'

        botToken = get_token(botName)
        
        botUrl = 'https://api.telegram.org/bot{}/{}'.format(botToken, methodName)
        options = {
            'chat_id' : chatId,
            'text' : textMessage
        }
        
        response = requests.post(
            url=botUrl,
            json=json.dumps(options)
            ).json

    return True