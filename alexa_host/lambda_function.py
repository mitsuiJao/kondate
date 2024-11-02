# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

import boto3
import json
import datetime
import locale

WEEKDAYJP = ["月", "火", "水", "木", "金", "土", "日"]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BUCKET_NAME = "kondate-json"
s3 = boto3.resource('s3')
s3client = boto3.client("s3")

def getJson(FILE_NAME):
    bucket = s3.Bucket(BUCKET_NAME)
    obj = bucket.Object(FILE_NAME)
    response = obj.get()    
    body = response['Body'].read()

    return json.loads(body.decode('utf-8'))

def datesearch(date):
    search = datetime.datetime.strptime(date, "%Y-%m-%d")
    res = s3client.list_objects_v2(Bucket=BUCKET_NAME)
    for f in res["Contents"]:
        delta = search - datetime.datetime.strptime(f["Key"].replace(".json", ""), "%Y%m%d")
        if delta < datetime.timedelta(days=7) and delta >= datetime.timedelta(days=0):
            return f["Key"]
    return None

def kondateSpeakout(j, date, when):
    whendoc = {"朝": "morning", "昼": "lunch", "夜": "dinner", "夕": "dinner"}
    menu = j["menu"]
    dwhen = datetime.datetime.strptime(date, "%Y-%m-%d")
    # mon0sum6 -> sum0thu6
    week = dwhen.weekday()+1
    week = week if week != 7 else 0
    kondateobj = menu[week]
    print(kondateobj)
    
    item = kondateobj["item"][whendoc[when]]
    speakweekday = WEEKDAYJP[dwhen.weekday()]
    speakdate = f"{dwhen.month}月{dwhen.day}日"
    A = item["A"]
    B = item["B"]
    common = item["common"]
    speakcommon = ""

    speak_output = f"{speakdate}{speakweekday}曜日の{when}ご飯の献立は"

    for s in common:
        speakcommon += s
        speakcommon += "、"

    if A != [] and B != []:
        speakA = ""
        speakB = ""
        for s in A:
            speakA += s
            speakA += "、"
        for s in B:
            speakB += s
            speakB += "、"
        
        speak_output += f"メニューA、{speakA} メニューB、{speakB} 共通メニューは"

    speak_output += speakcommon
    speak_output += "です。"
    print(speak_output)
    return speak_output


class kondateHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        logger.info("kondatehandler can_handle func called!")
        return ask_utils.is_intent_name("kondate")(handler_input)
    
    def handle(self, handler_input):
        enve = handler_input.request_envelope.to_dict()
        date = enve["request"]["intent"]["slots"]["date"]["value"]
        when = enve["request"]["intent"]["slots"]["when"]["value"]
        print(enve)
        FILE_NAME = datesearch(date)
        f = getJson(FILE_NAME)
        print(date)
        print(FILE_NAME)
        if f is None:
            speak_output = "献立が見つかりませんでした。"

        speak_output = kondateSpeakout(f, date, when)
        return handler_input.response_builder.speak(speak_output).response
    

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        logger.info("launchrequesthandler called!")
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "知りたい日にち、朝昼晩を教えてください"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# class HelloWorldIntentHandler(AbstractRequestHandler):
#     logger.info("helloworldintenthandler called!")

#     """Handler for Hello World Intent."""
#     def can_handle(self, handler_input):
#         # type: (HandlerInput) -> bool
#         return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

#     def handle(self, handler_input):
#         # type: (HandlerInput) -> Response
#         speak_output = "Hello World!"

#         return (
#             handler_input.response_builder
#                 .speak(speak_output)
#                 # .ask("add a reprompt if you want to keep the session open for the user to respond")
#                 .response
#         )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        logger.info("can_handle func of cancelorstopintenthandler was called!")        
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "うんこ!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(kondateHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
