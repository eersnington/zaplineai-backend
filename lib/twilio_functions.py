from dotenv import load_dotenv, find_dotenv
from twilio.twiml.voice_response import VoiceResponse, Start
from twilio.rest import Client
from fastapi import Request, WebSocket, WebSocketDisconnect, HTTPException
import asyncio
import os
import audioop
import base64
import json
import logging
import webrtcvad

from lib.audio_buffer import AudioBuffer
from lib.asr import transcribe_stream
from lib.call_chat import CallChatSession
from lib.db import db
from lib.custom_exception import CustomException

load_dotenv(find_dotenv(), override=True)


TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

# Constants
VAD_SAMPLERATE = 8000 # Hz
IGNORE_DURATION = 2  # seconds to ignore customer audio after bot response

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
TWILIO_PHONE_NUMBER = twilio_client.incoming_phone_numbers.list()[0]

active_calls = {}


def get_new_numbers() -> list:
    """
        Retrieves a list of new phone numbers in Twilio.

        Return: A list of phone numbers in Twilio.
    """
    return [phone.phone_number for phone in twilio_client.available_phone_numbers('US').local.list()]


async def get_available_numbers(get_first: bool) -> list:
    """
        Retrieves a list of all available (previously purchased but not used) phone numbers in Twilio Account.

        Return: A list of available phone numbers in Twilio.
    """
    twilio_phone_numbers = twilio_client.incoming_phone_numbers.list()

    db_numbers = await db.bot.find_many()

    # Retrieve all phone numbers associated with Bots from the database
    used_phone_numbers = [bot.phone_no for bot in db_numbers]

    available_numbers = []
    for phone in twilio_phone_numbers:
        if phone.phone_number not in used_phone_numbers:
            available_numbers.append(phone.phone_number)
            if get_first:
                return available_numbers

    return available_numbers


def buy_phone_number(phone_number: str) -> None:
    """
        Purchases a specific phone number in Twilio.

        Keyword arguments:
        phone_number -- The specific phone number to be purchased.

        Return: None. The function performs a purchase operation and does not return anything.
    """
    twilio_client.incoming_phone_numbers.create(phone_number=phone_number)


async def get_unused_phone_number() -> str:
    """
        Retrieves a list of all unused phone numbers by users in Twilio.

        Return: A new or unused phone number in Twilio.
    """
    available_numbers = await get_available_numbers(get_first=True)
    if available_numbers[0] is not None:
        return available_numbers[0]

    new_phone_number = get_new_numbers()[0]
    buy_phone_number(new_phone_number)
    return new_phone_number


def speech_delay(transcription_text: str) -> int:
    """
        Estimates the duration of a speech based on the number of words in the transcription.

        Keyword arguments:
        transcription_text -- The transcribed text to be spoken in the call.

        Return: The estimated duration of the speech in seconds.
    """
    return (len(transcription_text.split(" ")) / 2.5)


def update_phone(public_url: str, phone_number: str) -> None:
    """
        Updates the voice URL of a specific phone number in Twilio.

        Keyword arguments:
        public_url -- The public URL where Twilio will send a request when the phone number receives a call.
        phone_number -- The specific phone number to be updated.

        Return: None. The function performs an update operation and does not return anything.
    """
    phone = list(
        twilio_client.incoming_phone_numbers.list(phone_number=phone_number))
    if len(phone) == 0:
        raise Exception("No phone numbers found.")

    phone[0].update(
        voice_url=f"{public_url}/{phone_number}/call"
    )


async def voice_response(transcription_text: str, call_sid: str, twilio_client: Client) -> None:
    """
        Updates a call session with a transcribed text.

        Keyword arguments:
        transcription_text -- The transcribed text to be spoken in the call.
        call_sid -- The unique identifier of the call session to be updated.
        twilio_client -- The client instance used to interact with the Twilio API.

        Return: None. The function performs an update operation and does not return anything.
    """
    try:
        call_session = twilio_client.calls(call_sid)

        if call_session is None:
            raise Exception("Call session not found.")
        
        call_session.update(
            twiml=f'<Response><Say>{transcription_text}</Say><Pause length="60"/></Response>'
        )
    except Exception as e:
        logging.info(f"Exception: {e}")


async def call_accept(request:Request, public_url: str, phone_number: str) -> VoiceResponse:
    """
        Handles the initial call session.

        Keyword arguments:
        public_url -- The public URL where Twilio will send a request when the phone number receives a call.
        phone_number -- The specific phone number to be updated.
        brand_name -- The name of the brand for the call session.

        Return: A VoiceResponse instance containing the TwiML instructions for the call session.
    """
    form_data = await request.form()
    try:
        call_sid = form_data.get('CallSid')
        call_from = form_data.get('From')
    except Exception as e:
        raise CustomException(status_code=400, detail=str(e))
    
    active_calls[call_sid] = call_from

    response_text = f"Hey, my name is Zappy."
    response = VoiceResponse()
    start = Start()
    start.stream(
        url=f'wss://{public_url.split("//")[1]}/{phone_number}/stream')
    response.append(start)
    response.say(response_text)
    response.pause(length=60)
    return response


async def call_stream(websocket: WebSocket, phone_no: str, brand_name: str) -> None:
    """
    Handles the audio stream of a call session.

    Keyword arguments:
    websocket -- The websocket instance used to receive the audio stream from Twilio.
    phone_no -- The phone number of the incoming caller.
    brand_name -- The name of the brand for the call session.
    """
    is_bot_speaking = False
    is_speech_started = False

    audio_buffer = AudioBuffer() # _QueueStream() makes ASR unresponsive (bug)

    await websocket.accept()
    store = await db.bot.find_first(where={"phone_no": phone_no})

    vad = webrtcvad.Vad(3) # 3 is the aggressiveness mode

    initial_response = f" Thanks for calling {brand_name}!."

    llm_chat = CallChatSession(store.app_token, store.myshopify)
    call_sid = None

    try:
        while True:
            message = await websocket.receive_text()
            packet = json.loads(message)

            if packet['event'] == 'start':
                print('Media stream started!')
                call_sid = packet['start']['callSid']

                customer_phone_no = active_calls[call_sid]

                additional_response = llm_chat.start(call_sid, customer_phone_no)

                new_response = initial_response + additional_response
                print(f"New Response: {new_response}")

                delay = speech_delay("Hey, my name is Zap.")
                print(f"Speech Delay: {delay}s")
                await asyncio.sleep(delay)
                print("Bot response completed")

                await voice_response(new_response, call_sid, twilio_client)
                delay = speech_delay(new_response)
                print(f"Speech Delay: {delay}s")
                await asyncio.sleep(delay)
                print("Bot response completed")

            elif packet['event'] == 'stop':
                print('Media stream stopped!')
                print("Call Intent: ", llm_chat.get_call_intent())
                llm_chat.update_call_status(store.userId, llm_chat.get_call_intent())

            elif packet['event'] == 'media':
                chunk = base64.b64decode(packet['media']['payload'])
                audio_data = audioop.ulaw2lin(chunk, 2)
                is_speech = vad.is_speech(audio_data, VAD_SAMPLERATE)
                audio_data = audioop.ratecv(audio_data, 2, 1, 8000, 16000, None)[0] # for phone calls, not browser calls

                if is_speech:
                    if not is_bot_speaking:
                        is_speech_started = True
                        audio_buffer.write(audio_data)
                    else:
                        audio_buffer.clear()
                else:
                    if is_speech_started:
                        is_speech_started = False

                        print("Processing buffered audio...")
                        transcription_result = transcribe_stream(audio_buffer)
                        print(f"Transcription: {transcription_result}")
                        audio_buffer.clear()

                        if transcription_result is not None:
                            llm_response = llm_chat.get_response(transcription_result)
                            print(f"LLM Response: {llm_response}")

                            delay = speech_delay(llm_response)
                            print(f"Speech Delay: {delay}s")

                            await voice_response(llm_response, call_sid, twilio_client)
                            print("Audio Buffer Size: ", audio_buffer.size())
                            is_bot_speaking = True
                            await asyncio.sleep(delay)
                            is_bot_speaking = False
                            print("Bot response completed")
                            print("Audio Buffer Size: ", audio_buffer.size())

    except WebSocketDisconnect:
        logging.info("WebSocket disconnected")
    except HTTPException as e:
        logging.info(f"HTTP Exception: {e}")
    except Exception as e:
        logging.info(f"Exception: {e}")
        logging.info(f"{e.__traceback__}")
        response = f"Sorry, we are currently experiencing technical difficulties. Please call again later."
        await voice_response(response, call_sid, twilio_client)