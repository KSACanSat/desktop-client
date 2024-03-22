from threading import Thread
from serial import Serial
from time import sleep
from io_stream import Stream

"""
A soros kommunikáció kezeléséhez tartozó osztályok helye.
"""


class SerialThread(Thread):
    """
    A soros kommunikációt futtató thread reprezentációja.
    """

    def __init__(self, conn, data_callback):
        """
        :param conn: serial.Serial - a pyserial soros kapcsolat
        :param data_callback: Az új adat érkezésekor meghívandó függvény
        """
        super().__init__()
        self.running = True
        self.conn = conn
        self.data_callback = data_callback
        self.start()

    def run(self):
        """
        A szálon végrehajtandó művelet, jelen esetben a soros porton beérkező adatok továbbküldése amíg fut a program.
        Hiba esetén a végrehajtás leáll.

        **TODO: Hibakezelés javítása, esetleg UI szinten is**
        """
        while self.running:
            try:
                self.data_callback(self.conn.readline())
            except Exception:
                break

    def stop(self):
        """
        A szál leállítója
        """
        self.running = False


class UnsupportedProtocolError(IOError):
    """
    A hibás protokollt jelző hiba
    """
    @staticmethod
    def new():
        """
        :return: egy új UnsupportedProtocolError osztály
        """
        return UnsupportedProtocolError("", "")

    def __init__(self, t, __obj):
        super.__init__(t, __obj)


class SerialStream(Stream):
    """
    Stream implementation for serial communication.
    :see: Stream
    """
    def __init__(self, device):
        """
        Parameters
        ----------
        device: device.Device
            The device to connect to
        """
        self.conn = Serial(device.port, device.baud)
        self.thread = SerialThread(self.conn, self.__data_receiver)
        self.info = {}

    def __data_receiver(self, data):
        """
        Callback for `self.thread`
        Parameters
        ----------
        data: bytearray
            The unprocessed serial data
        """
        self.info = data.decode('utf-8')

    def get_message(self):
        """
        Fetch the latest data that we received from the serial port

        :returns: The unformatted packet data as string
        """
        # Wait for data if there isn't any ( for 0.2s each try )
        if len(self.info) == 0:
            sleep(0.2)
            return self.get_message()
        return self.info

    def get_type(self):
        return "serial"

    def stop(self):
        """
        Closes the serial communication
        """
        self.thread.stop()
        self.conn.close()
