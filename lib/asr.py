import io
import os
import tempfile
import wave
import logging
from lib.audio_buffer import AudioBuffer, _QueueStream, _TwilioSource
from faster_whisper import WhisperModel
import torch
from transformers import pipeline
from transformers.utils import is_flash_attn_2_available
import speech_recognition as sr
from pydub import AudioSegment

from dotenv import load_dotenv
import functools

load_dotenv()
logging.getLogger().setLevel(logging.INFO)

model_size = "small"

@functools.cache
def get_model():
    # STTmodel = WhisperModel(model_size, device="cuda",
    #                         compute_type="int8_float16")
    pipe = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-large-v3", # select checkpoint from https://huggingface.co/openai/whisper-large-v3#model-details
        torch_dtype=torch.bfloat16,
        device="cuda:0", # or mps for Mac devices
        model_kwargs={"attn_implementation": "flash_attention_2"} if is_flash_attn_2_available() else {"attn_implementation": "sdpa"},
    )   
    return pipe

# Initialize faster_whisper model

if os.getenv("PRODUCTION_MODE") == "False":
    logging.info("Skipping model loading in development environment")
    STTmodel = None

else:
    logging.info(f"Loading Whisper Model | Size: {model_size}")
    STTmodel = get_model()
    logging.info("Loading completed!")


recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.pause_threshold = 2.5
recognizer.dynamic_energy_threshold = False


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

def transcribe_stream(audio_stream: _QueueStream) -> str:
    """
        Transcribes audio from a byte stream into text.

        Keyword arguments:
        audio_stream -- The byte stream containing audio data to be transcribed.
    """
    with _TwilioSource(audio_stream) as source:
        with tempfile.TemporaryDirectory() as tmp:
            logging.info("Waiting for twilio caller...")
            tmp_path = os.path.join(tmp, "mic.wav")
            try:
                audio = recognizer.listen(source, timeout=10)
                logging.info("Audio received from twilio caller.")
                data = io.BytesIO(audio.get_wav_data())
                audio_clip = AudioSegment.from_file(data)
                audio_clip.export(tmp_path, format="wav")

                if STTmodel is None:
                    return "Model not loaded"
                
                # segments, info = STTmodel.transcribe(tmp_path, language="en", task="transcribe")

                # transcription = ''
                # for segment in segments:
                #     transcription += segment.text

                outputs = STTmodel(
                    "audio.wav",
                    chunk_length_s=30,
                    batch_size=24,
                    return_timestamps=False,
                )

                transcription = outputs["text"]

                return transcription
            except Exception as e:
                logging.error(f"Error in transcribing audio: {e}")
                return None
    
