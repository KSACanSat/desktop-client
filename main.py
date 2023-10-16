from tkinter import *
from serial_comm import SerialManager
from time import sleep


class App:
    def __init__(self):
        self.serial = SerialManager("COM8", 9600)
        # MAIN WINDOW SETUP
        self.root = Tk()
        self.root.geometry = "600x800"
        # GUI SETUP
        self.scrollbar = Scrollbar(self.root)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.info_box = Listbox(self.root, yscrollcommand=self.scrollbar.set)
        self.info_box.pack(side=LEFT, fill=BOTH)
        self.scrollbar.config(command=self.info_box.yview)

    def query_serial(self):
        message = self.serial.get()
        self.info_box.insert(END, message)
        self.root.after(10, self.query_serial)

    def show(self):
        self.query_serial()
        self.root.mainloop()

    def stop(self):
        self.serial.stop()


if __name__ == "__main__":
    app = App()
    try:
        app.show()
    finally:
        app.stop()
