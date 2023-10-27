from serial_comm import SerialManager
from screens import *
from tkinter import Tk, TclError


class App(object):
    _instance = None
    """
    A főablak osztálya
    """

    @classmethod
    def new(cls):
        if cls._instance is None:
            cls._instance = App()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            App.new()
        return cls._instance

    def __init__(self):
        self.serial = SerialManager("COM8", 9600)
        self.last_time = 0
        # UI setup
        self.schedule_window = Tk()
        self.raw_window = RawInfoScreen(self.stop)

    def query_serial(self):
        """
            A soros kommunikáció eredményeinek megjelenése
        """
        message = self.serial.get()
        if self.last_time != message["time"]:
            self.raw_window.add_row(message)
            self.last_time = message["time"]
        self.schedule_window.after(200, self.query_serial)

    def show(self):
        """
            Az appot elindító kód
        """
        self.schedule_window.withdraw()
        self.query_serial()
        self.raw_window.show()

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


if __name__ == "__main__":
    try:
        App.get_instance().show()
    finally:
        App.get_instance().stop("execution")
