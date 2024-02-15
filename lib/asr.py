import os
import wave
import logging
from lib.audio_buffer import AudioBuffer
from faster_whisper import WhisperModel
from dotenv import load_dotenv
import functools

load_dotenv()
logging.getLogger().setLevel(logging.INFO)

model_size = "large-v3"

@functools.cache
def get_model():
    STTmodel = WhisperModel(model_size, device="cuda",
                            compute_type="int8_float16")
    return STTmodel

# Initialize faster_whisper model

if os.getenv("PRODUCTION_MODE") == "False":
    logging.info("Skipping model loading in development environment")
    STTmodel = None

else:
    logging.info(f"Loading Whisper Model | Size: {model_size}")
    STTmodel = get_model()
    logging.info("Loading completed!")



def transcribe_buffer(audio_buffer: AudioBuffer) -> str:
    """
        Transcribes audio from an AudioBuffer into text.

        Keyword arguments:
        audio_buffer -- The buffer containing audio data to be transcribed.

        Return: The transcription of the audio in the buffer as a string.
    """

    if STTmodel is None:
        return "Model not loaded"

    temp_audio_file = 'temp_audio.wav'
    temp_audio_path = os.path.join(os.getcwd(), temp_audio_file)

    with wave.open(temp_audio_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(audio_buffer.read())

    # Pass the audio file to Whisper for transcription
    with open(temp_audio_path, 'rb') as audio_file:
        segments, info = STTmodel.transcribe(audio_file, language="en", beam_size=5, task="transcribe")

        transcription = ''
        for segment in segments:
            transcription += segment.text

    return transcription
