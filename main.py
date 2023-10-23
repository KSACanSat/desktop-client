from tkinter import *
from serial_comm import SerialManager
from result_table import ResultTable


class App:
    """
    A főablak osztálya
    """
    def __init__(self):
        self.serial = SerialManager("COM8", 9600)
        self.last_time = 0
        # MAIN WINDOW SETUP
        self.root = Tk()
        # GUI SETUP
        self.table = ResultTable(self.root, {"time": "Idő", "sensor1": "1. műszer"}, "time")
        self.table.pack()

    def query_serial(self):
        """
            A soros kommunikáció eredményeinek megjelenése
        """
        message = self.serial.get()
        if self.last_time != message["time"]:
            self.table.add_data(message)
            self.last_time = message["time"]
        self.root.after(200, self.query_serial)  # Futtatás 0.2 sec múlva

    def show(self):
        """
            Az appot elindító kód
        """
        self.query_serial()
        self.root.mainloop()

    def stop(self):
        """
            A leállító kód
        """
        self.serial.stop()


if __name__ == "__main__":
    app = App()
    try:
        app.show()
    finally:
        app.stop()
