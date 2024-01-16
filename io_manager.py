from io_stream import Stream
import _io


class FileStream(Stream):

    def __init__(self, path, mode="plain"):
        self.file = open(path, "r")
        self.mode = mode
        self.content = []
        self.index = 0

    @property
    def get_type(self):
        return "file_" + self.mode

    def get_message(self):
        if len(self.content) == 0:
            self.content = self.file.read().split('\n')[:-1]
        msg = self.content[self.index if self.index < len(self.content) else len(self.content) - 1]
        if self.index < len(self.content):
            self.index += 1
        return msg

    def stop(self):
        self.file.close()


class IOManager:
    def __init__(self):
        self.stream: Stream = None
        self.file: _io.TextIOWrapper = None

    def set_stream(self, stream: Stream):
        self.stream = stream

    def set_path(self, path):
        try:
            self.file = open(path, "w+")
            return True
        except IOError:
            return False

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
