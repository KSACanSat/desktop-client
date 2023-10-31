from serial_comm import SerialManager
import tkthread; tkthread.patch()
from screens import *
from tkinter import Tk, TclError


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
        self.serial = SerialManager("COM9", 9600)
        self.last_time = 0
        # UI setup
        self.schedule_window = Tk()
        self.welcome_window = WelcomeScreen(self.schedule_window, self.attempt_connect)
        self.connect_window = ConnectingScreen(self.schedule_window)
        self.raw_window = RawInfoScreen(self.schedule_window, self.stop)

    def query_serial(self):
        """
            A soros kommunikáció eredményeinek megjelenése
        """
        message = self.serial.get()
        if self.last_time != message["time"]:
            self.raw_window.add_row(message)
            self.last_time = message["time"]
        self.schedule_window.after(200, self.query_serial)

    def attempt_connect(self, port, baud):
        print("got datas")
        self.connect_window.set_data(port, baud)
        print("set them")
        self.connect_window.show()
        print("started connect window")
        self.connect_window.show()
        print("called")

    def show(self):
        """
            Az appot elindító kód
        """
        self.schedule_window.withdraw()
        # self.query_serial()
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
        self.serial.stop()
        if close_id != "raw_window":
            self.raw_window.close()
