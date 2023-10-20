from threading import Thread
from serial import Serial
from time import sleep


class SerialThread(Thread):
    def __init__(self, conn, data_callback):
        super().__init__()
        self.running = True
        self.conn = conn
        self.data_callback = data_callback
        self.start()

    def run(self):
        while self.running:
            try:
                self.data_callback(self.conn.readline())
            except Exception:
                break

    def stop(self):
        self.running = False


class UnsupportedProtocolError(IOError):
    @staticmethod
    def new():
        return UnsupportedProtocolError("", "")

    def __init__(self, t, __obj):
        super.__init__(t, __obj)


class SerialManager:
    def __init__(self, port, band):
        self.conn = Serial(port, band)
        self.thread = SerialThread(self.conn, self.data_receiver)
        self.info = {}

    def data_receiver(self, data):
        raw_info = bytes(data).decode().split("\r\n")[0]
        if "&" not in raw_info or "=" not in raw_info:
            raise UnsupportedProtocolError.new()
        raw_pairs = raw_info.split("&")
        current_data = {k: v for k, v in (raw_pair.split("=") for raw_pair in raw_pairs)}
        self.info = current_data

    def get(self):
        if len(self.info) == 0:
            sleep(0.2)
            return self.get()
        return self.info

    def stop(self):
        self.thread.stop()
        self.conn.close()
