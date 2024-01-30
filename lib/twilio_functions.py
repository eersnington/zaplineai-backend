from dotenv import load_dotenv
from twilio.twiml.voice_response import VoiceResponse, Start
from twilio.rest import Client
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
import os
import audioop
import base64
import json

from lib.audio_buffer import AudioBuffer
from lib.asr import transcribe_buffer

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
TWILIO_PHONE_NUMBER = twilio_client.incoming_phone_numbers.list()[0]


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

    phone.update(
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
    call_session = twilio_client.calls(call_sid)

    if call_session is None:
        raise Exception("Call session not found.")
    call_session.update(
        twiml=f'<Response><Say>{transcription_text}</Say><Pause length="60"/></Response>'
    )


async def call_accept(public_url: str, phone_number: str) -> VoiceResponse:
    response = VoiceResponse()
    start = Start()
    start.stream(
        url=f'wss://{public_url.split("//")[1]}/{phone_number}/stream')
    response.append(start)
    response.say('Hello. How may I help you today?')
    response.pause(length=60)
    return response


async def call_stream(websocket: WebSocket) -> None:
    audio_buffer = AudioBuffer()
    buffer_threshold = 16000  # Initial buffer threshold
    call_sid = None

    await websocket.accept()

    try:
        while True:
            message = await websocket.receive_text()
            packet = json.loads(message)

            if packet['event'] == 'start':
                print('Media stream started!')
                call_sid = packet['start']['callSid']
            elif packet['event'] == 'stop':
                print('Media stream stopped!')

            if packet['event'] == 'media':
                chunk = base64.b64decode(packet['media']['payload'])
                # Convert audio data from ulaw to linear PCM
                audio_data = audioop.ulaw2lin(chunk, 2)
                # Convert audio data from 8kHz to 16kHz for Whisper
                audio_data = audioop.ratecv(
                    audio_data, 2, 1, 8000, 16000, None)[0]
                # Compute audio energy
                audio_energy = audioop.rms(audio_data, 2)
                energy_threshold = 700

                if audio_energy >= energy_threshold:
                    audio_buffer.append(audio_data)

                if len(audio_buffer) >= buffer_threshold:
                    transcription_result = transcribe_buffer(audio_buffer)
                    print("Transcription:", transcription_result)
                    # Clear the buffer after transcription
                    audio_buffer.clear()
                    print(f"Call SID: {call_sid}")
                    await voice_response(transcription_result, call_sid)

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except HTTPException as e:
        print(f"HTTP Exception: {e}")
    except Exception as e:
        print(f"Exception: {e}")
