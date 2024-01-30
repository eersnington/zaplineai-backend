from audio_buffer import AudioBuffer
import os
import wave

from faster_whisper import WhisperModel

# Initialize faster_whisper model
model_size = "small"
STTmodel = WhisperModel(model_size, device="cuda", compute_type="int8_float16")


def transcribe_buffer(audio_buffer: AudioBuffer) -> str:
    """
        Transcribes audio from an AudioBuffer into text.

        Keyword arguments:
        audio_buffer -- The buffer containing audio data to be transcribed.

        Return: The transcription of the audio in the buffer as a string.
    """

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
