import queue

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

    def size(self) -> int:
        return self.q.qsize()
    
    def clear(self):
        self.q.queue.clear()
    
