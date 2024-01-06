from abc import abstractmethod
from serial_comm import SerialManager


class Stream:
    @abstractmethod
    def get_message(self):
        pass

    @abstractmethod
    def stop(self):
        pass


class SerialStream(Stream):
    def __init__(self, serial: SerialManager):
        self.serial = serial

    def get_message(self):
        return self.serial.get()

    def stop(self):
        self.serial.stop()


class IOManager:
    def __init__(self):
        self.stream: Stream = None

    def set_stream(self, stream: Stream):
        self.stream = stream

    def get_message(self):
        return self.stream.get_message()