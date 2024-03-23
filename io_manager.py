from io_stream import Stream
import _io
from device import Device


class FileStream(Stream):
    """
    Stream implementation for the recorded data stored in text files.
    :see: Stream
    """
    def __init__(self, path):
        """
        Parameters:
        -----------
        path: str
            Path to the text file
        """
        self.file = open(path, "r")
        self.content = []
        self.index = 0

    @property
    def get_type(self):
        return "file"

    def get_message(self):
        """
        Gets the current message from the text
        """
        if len(self.content) == 0:
            self.content = self.file.read().split('\n')[:-1]
        msg = self.content[self.index if self.index < len(self.content) else len(self.content) - 1]
        if self.index < len(self.content):
            self.index += 1
        return msg

    def stop(self):
        self.file.close()


class IOManager:
    """
    Manager class for all IO activities
    """
    def __init__(self):
        self.stream: Stream = None
        self.device: Device = None
        self.file: _io.TextIOWrapper = None

    def set_stream(self, data):
        """
        Activates the current stream object and device
        Parameters:
            data: dict
                In this param you need to pass a stream as "stream" and a device as "device"
        """
        self.stream = data["stream"]
        self.device = data["device"]

    def set_path(self, path):
        """
        Sets the recording path
        Parameters:
            path: str
                Path to recording (might not exist, in this case we create the file)
        Returns:
            boolean based on the success of opening the file
        """
        try:
            self.file = open(path, "w+")
            return True
        except IOError:
            return False

    def get_message(self):
        """
        UI safe, abstract way of getting a packet.
        Returns:
            a list of float - aka packet
        """
        raw_message = self.stream.get_message()
        # Writes into the recording if set it earlier (using the `set_path` method)
        if self.file is not None:
            self.file.write(raw_message)

        raw_pairs = raw_message.split("\t")
        return [float(raw_pair) if "\n" not in raw_pair and len(raw_pair) > 0 else 0.00 for raw_pair in raw_pairs][:-1]

    def stop(self):
        """
        Stops IO activity
        """
        if self.stream is not None:
            self.stream.stop()
        if self.file is not None:
            self.file.close()
