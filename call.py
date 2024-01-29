# Install required packages
# pip install fastapi twilio pyngrok 'uvicorn[standard]' python-multipart
import logging
from twilio.rest import Client
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather, Start
import base64
import os
import json
import audioop
import wave
from pyngrok import ngrok
from faster_whisper import WhisperModel

app = FastAPI()

# Configure Twilio credentials
TWILIO_ACCOUNT_SID = ""
TWILIO_AUTH_TOKEN = ""

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Initialize ngrok
ngrok.set_auth_token("")

# Create ngrok tunnel
port = 5055
public_url = ngrok.connect(port, bind_tls=True).public_url

# Configure Twilio phone number with ngrok public URL
TWILIO_PHONE_NUMBER = twilio_client.incoming_phone_numbers.list()[0]
TWILIO_PHONE_NUMBER.update(
    voice_url=f"{public_url}/call/{TWILIO_PHONE_NUMBER.phone_number}"
)

# Initialize faster_whisper model
model_size = "small"
STTmodel = WhisperModel(model_size, device="cuda", compute_type="int8_float16")


class AudioBuffer:
    """Buffer to store audio data."""

    def __init__(self):
        self.buffer = b''

    def append(self, data):
        self.buffer += data

    def read(self):
        return self.buffer

    def clear(self):
        self.buffer = b''

    def __len__(self):
        return len(self.buffer)

    def __str__(self):
        return self.buffer


@app.post("/call")
async def call():
    """Accept a phone call."""
    print("Call incoming!")
    response = VoiceResponse()
    start = Start()
    start.stream(url=f'wss://{public_url.split("//")[1]}/stream')
    response.append(start)
    response.say('Hello. How may I help you today?')
    response.pause(length=60)
    return Response(content=str(response), media_type="application/xml")


@app.websocket("/stream")
async def stream(websocket: WebSocket):
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


def transcribe_buffer(audio_buffer: AudioBuffer):
    temp_audio_file = 'temp_audio.wav'
    temp_audio_path = os.path.join(os.getcwd(), temp_audio_file)

    with wave.open(temp_audio_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(audio_buffer.read())

    # Pass the audio file to Whisper for transcription
    with open(temp_audio_path, 'rb') as audio_file:
        segments, info = STTmodel.transcribe(
            audio_file, beam_size=5, task="transcribe")

        transcription = ''
        for segment in segments:
            transcription += segment.text

    return transcription


async def voice_response(transcription_text: str, call_sid: str):
    call_session = twilio_client.calls(call_sid)
    call_session.update(
        twiml=f'<Response><Say>{transcription_text}</Say><Pause length="60"/></Response>'
    )

if __name__ == "__main__":
    import uvicorn
    print(f"Waiting for calls on: {TWILIO_PHONE_NUMBER.phone_number}")
    print(f"Twilio phone number updated with ngrok URL: {public_url}")

    uvicorn.run(app, host="0.0.0.0", port=port)
