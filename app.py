from serial_comm import SerialStream
from io_manager import *
from screens import *
from tkinter import Tk, TclError
from screens.result_renderer.diagram import Diagram


class App(object):
    _instance = None
    """
    Az applikációt megtestesítő statikus osztály.
    A hozzáféréshez hívd meg a `get_instance` függvényt!
    """

    @classmethod
    def new(cls):
        """
        Létrehoz egy új példányt az appból, ha még nem létezett volna...
        """
        if cls._instance is None:
            cls._instance = App()

    @classmethod
    def get_instance(cls):
        """
        Lekérdezi az osztály pélányát...
        """
        cls.new()
        return cls._instance

    def __init__(self):
        self.io = IOManager()
        self.last_time = 0
        # UI setup
        self.schedule_window = Tk()
        self.welcome_window = WelcomeScreen(self.schedule_window, self.attempt_connect, self.stop)
        self.connect_window = ConnectingScreen(self.schedule_window, self.set_serial_conn)
        self.raw_window = RawInfoScreen(self.schedule_window, self.stop, self.set_path)
        self.result = ResultScreen(self.schedule_window, 2, 2,
                                   [Diagram(0, 0, "Hőmérséklet", [0])])

    def attempt_connect(self, data):
        """
        Elindítja a kapcsolódást kezelő ablakot
        :param port A soros port
        :param baud A baud rate
        """
        if data["type"] == "serial":
            self.connect_window.set_data(data["data"][0], data["data"][1])
            self.connect_window.show()
        elif data["type"] == "recording":
            self.io.set_stream(FileStream(data["data"], "plain"))
            self.welcome_window.hide()
            self.raw_window.disable_saving()
            self.raw_window.show()
            self.query_serial()

    def set_serial_conn(self, serial: SerialStream):
        """
        Beállítja a soros kommunikációt és elindítja a táblázatot.
        :param serial A soros kommunikáció
        """
        self.io.set_stream(serial)
        self.welcome_window.hide()
        self.raw_window.show()
        self.query_serial()

    def set_path(self, path):
        self.io.set_path(path)

    def query_serial(self):
        """
            A soros kommunikáció eredményeinek megjelenése
        """
        message = self.io.get_message()
        if message[0] > self.last_time:
            self.raw_window.add_row(message)
            self.result.add_result(message)
            self.last_time = message[0]
        self.schedule_window.after(200 if self.io.stream.get_type == "serial" else 20, self.query_serial)

    def show(self):
        """
            Az appot elindító kód
        """
        self.schedule_window.withdraw()
        self.raw_window.hide()
        self.connect_window.hide()
        self.welcome_window.show()
        self.schedule_window.mainloop()

    def stop(self, close_id):
        """
            A leállító kód
        """
        try:
            self.schedule_window.destroy()
        except TclError:
            pass
        self.io.stop()
        if close_id != "raw_window":
            self.raw_window.close()
