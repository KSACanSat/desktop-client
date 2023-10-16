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


class SerialManager:
    def __init__(self, port, band):
        self.conn = Serial(port, band)
        self.thread = SerialThread(self.conn, self.data_receiver)
        self.info = ""

    def data_receiver(self, data):
        self.info = str(data)

    def get(self):
        if self.info == "":
            sleep(0.01)
            return self.get()
        return self.info

    def stop(self):
        self.thread.stop()
        self.conn.close()
