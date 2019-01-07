"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
from urllib.request import urlopen
import re
import datetime


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'Ritardo treni stazione di Arosio',
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    session_attributes = {}
    card_title = "Benvenuto"
    speech_output = "Benvenuto nella skill Alexa, se vuoi sapere il ritardo del tuo treno basta chiederlo. Prova a dire 'Qual è il ritardo del mio treno?' oppure 'Il  treno è in orario?'."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Se vuoi sapere il ritardo del tuo treno basta chiederlo"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Sessione terminata"
    speech_output = "Grazie per aver provato la skill."
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def getTrainDelayResponse(intent, session):
    session_attributes = {}
    reprompt_text = None
    
    #-----------------------
    trains = {"06:05" : 612, "06:35" : 1614, "07:05" : 618, "07:35" : 1622, "08:05" : 624, "08:35" : 2626, "09:05" : 628, "10:05" : 632, "11:05" : 636, "12:05" : 640, "13:05" : 644, 
			"13:35" : 1646, "14:05" : 648, "14:35" : 1650, "15:05" : 652, "15:35" : 2654, "16:05" : 656, "16:35" : 2660, "17:05" : 662, "17:35" : 2666, "18:05" : 668, "18:35" : 1670}

    non_existing = ["09:35", "10:35", "11:35", "12:35"]
    
    utc = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    hour = utc.hour
    minute = utc.minute
    
    # i treni passano alle :35 o alle :05. Così facendo scelgo il prossimo treno, con un po' di margine
    if minute >= 50:
    	minute = 5
    	hour += 1
    elif minute >= 20 and minute < 50:
    	minute = 35
    elif minute >=0 and minute <20: 
    	minute = 5
    
    time = str(hour).zfill(2) + ':' + str(minute).zfill(2)
    
    if time not in non_existing and time in trains:
    	train = trains[time]
    
    	html = urlopen("http://mobile.my-link.it/mylink/mobile/scheda?numeroTreno=" + str(train) + "&codLocOrig=N00079&tipoRicerca=stazione&lang=IT").read().decode('utf-8')
    
    	beginning = html.find('<div  class="evidenziato"><strong>') + len('<div  class="evidenziato"><strong>')
    	end = html.find('<!--c:if test="$') - 23
    	content = html[beginning:end]
    
    	content = re.sub("\s\s+", " ", str(content))[1:]
    	content = content.replace("e&#039;", 'è')
    	content = str(content).strip()
    else:
    	content = "Nessun treno previsto a breve nella fascia oraria 6.05 - 18.05. Per gli orari degli altri treni consultare il sito di Trenord."
    	
    speech_output = str(content)
    should_end_session = True
    #-----------------------
    
    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
    
    # avviato quando l'utente avvia la skilll senza dire cosa vuole. Viene
    # avviato il messaggio di benvenuto
    
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    
    # controllo degli intent per la skill

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "getTrainDelay":
        return getTrainDelayResponse(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])

# --------------- Main handler ------------------

def lambda_handler(event, context):
    #if event['session']['new']:
     #   on_session_started({'requestId': event['request']['requestId']},
      #                     event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
