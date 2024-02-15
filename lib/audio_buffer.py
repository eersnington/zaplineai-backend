import io
import os
import tempfile
import queue
import logging

from pydub import AudioSegment
import speech_recognition as sr

class AudioBuffer:
    """
    The AudioBuffer class is used to store audio data.
    """

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
    

class _TwilioSource(sr.AudioSource):
    def __init__(self, stream):
        self.stream = stream
        self.CHUNK = 1024
        self.SAMPLE_RATE = 8000
        self.SAMPLE_WIDTH = 2

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class _QueueStream:
    def __init__(self):
        self.q = queue.Queue(maxsize=-1)

    def read(self, chunk: int) -> bytes:
        return self.q.get()

    def write(self, chunk: bytes):
        self.q.put(chunk)

# nvidia-smi | grep 'python' | awk '{ print $5 }' | xargs -n1 kill -9
class WhisperTwilioStream:
    def __init__(self, whisper_model):
        self.audio_model = whisper_model
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.pause_threshold = 2.5
        self.recognizer.dynamic_energy_threshold = False
        self.stream = None

    def get_transcription(self) -> str:
        self.stream = _QueueStream()
        with _TwilioSource(self.stream) as source:
            logging.info("Waiting for twilio caller...")
            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = os.path.join(tmp, "mic.wav")
                audio = self.recognizer.listen(source)
                data = io.BytesIO(audio.get_wav_data())
                audio_clip = AudioSegment.from_file(data)
                audio_clip.export(tmp_path, format="wav")
                result = self.audio_model.transcribe(tmp_path, language="english")
        predicted_text = result["text"]
        self.stream = None
        return predicted_text