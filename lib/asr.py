import io
import os
import tempfile
import wave
import logging
from lib.audio_buffer import AudioBuffer, _QueueStream, _TwilioSource
import torch
from transformers import pipeline
from transformers.utils import is_flash_attn_2_available
import speech_recognition as sr
from pydub import AudioSegment

from dotenv import load_dotenv
import functools

load_dotenv()
logging.getLogger().setLevel(logging.INFO)

model_name = "openai/whisper-large-v3" #"openai/whisper-large-v3"

@functools.cache
def get_model():
    pipe = pipeline(
        "automatic-speech-recognition",
        model=model_name, # select checkpoint from https://huggingface.co/openai/whisper-large-v3#model-details
        torch_dtype=torch.bfloat16,
        device="cuda:0", # or mps for Mac devices
        model_kwargs={"attn_implementation": "flash_attention_2"} if is_flash_attn_2_available() else {"attn_implementation": "sdpa"},
    )   
    return pipe

# Initialize whisper model

if os.getenv("PRODUCTION_MODE") == "False":
    logging.info("Skipping model loading in development environment")
    STTmodel = None

else:
    logging.info(f"Loading Whisper Model | Model Name: {model_name}")
    STTmodel = get_model()
    logging.info("Loading completed!")


recognizer = sr.Recognizer()
recognizer.energy_threshold = 700  
recognizer.pause_threshold = 0.8
recognizer.dynamic_energy_threshold = False


def transcribe_stream(audio_stream: AudioBuffer) -> str:
    """
        Transcribes audio from a byte stream into text.

        Keyword arguments:
        audio_stream -- The byte stream containing audio data to be transcribed.
    """
    with _TwilioSource(audio_stream) as source:
        with tempfile.TemporaryDirectory() as tmp:
            #logging.info("Waiting for twilio caller...")
            tmp_path = os.path.join(tmp, "mic.wav")
            try:
                audio = recognizer.listen(source, timeout=10)
                #logging.info("Audio received from twilio caller.")
                data = io.BytesIO(audio.get_wav_data())
                audio_clip = AudioSegment.from_file(data)
                audio_clip.export(tmp_path, format="wav")

                if STTmodel is None:
                    return "Model not loaded"

                outputs = STTmodel(
                    tmp_path,
                    chunk_length_s=30,
                    batch_size=24,
                    return_timestamps=False,
                )

                transcription = outputs["text"]
                if transcription == " you" or transcription == " Thank you." or len(transcription) < 2:
                    return None

                return transcription
            except Exception as e:
                logging.error(f"Error in transcribing audio: {e}")
                return None
    
