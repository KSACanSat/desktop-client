from threading import Thread
from serial import Serial
from time import sleep
from io_stream import Stream
import re

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
    A soros kommunikációt kezelő UI-safe osztály
    (olyan szintje a soros kommunikáció vezérlésének, ami nem blokkolja az ablakainkat)
    """
    def __init__(self, port, baud_rate):
        """
        :param port: Az OS által kirendelt soros port
        :param baud_rate: A földi állomáson megadott baud rate

        **TODO: Kapcsolódási hibák jelzése a UI szintjén (#2)**
        """
        self.conn = Serial(port, baud_rate)
        self.thread = SerialThread(self.conn, self.data_receiver)
        self.rex = re.compile("[0-9]|\t|\.|-")
        self.info = ""

    def data_receiver(self, data: bytes):
        """
        A soros kommunikációs szál callbackja.
        :param data: A `SerialThread` által beolvasott adat
        """
        self.info = str(data)

    def get_message(self):
        """
        A legutóbbi adat lekérdezése ami beérkezett a földi rádióállomásunkról
        :return: A legutóbbi üzenet formázott változata
        """
        # Ha nincs üzenet, várakozás amíg nem jön egy (0.2 másodpercenként ellenőrzés)
        if not self.info:
            sleep(0.2)
            return self.get_message()
        packet = self.info.replace("'", "").replace("\\r\\n", "").replace("\\t", "\t")[1:]
        regex = ''.join(self.rex.findall(packet))
        if regex != packet:
            print("Corrupted packet:", packet)
            self.info = ""
            return self.get_message()
        return packet

    def get_type(self):
        return "serial"

    def stop(self):
        """
        A soros kommunikáció leállítója
        """
        self.thread.stop()
        self.conn.close()
