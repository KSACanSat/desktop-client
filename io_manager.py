from io_stream import Stream
from serial_comm import SerialStream
import os, _io


class IOManager:
    def __init__(self):
        self.stream: Stream = None
        self.file: _io.TextIOWrapper = None

    def set_stream(self, stream: Stream):
        self.stream = stream

    def set_path(self, path):
        exists = os.path.exists(path)
        if exists:
            self.file = open(path, "a")
        return exists

    def get_message(self):
        raw_message = self.stream.get_message()

        if self.file is not None:
            self.file.write(raw_message)

        raw_pairs = raw_message.split(";")[:-1]
        return [float(raw_pair) for raw_pair in raw_pairs]

    def stop(self):
        self.stream.stop()
        if self.file is not None:
            self.file.close()
