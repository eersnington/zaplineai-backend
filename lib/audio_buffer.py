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
