from tkinter import *
from .result_table import ResultTable


class RawInfoScreen:
    def __init__(self, on_close):
        self.visible = False
        self.on_close_handler = on_close
        # MAIN WINDOW SETUP
        self.root = Tk()
        # GUI SETUP
        self.table = ResultTable(self.root, {"time": "Idő", "sensor1": "1. műszer"}, "time")
        self.table.pack()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def add_row(self, row):
        if self.visible:
            self.table.add_data(row)

    def show(self):
        self.visible = True
        self.root.mainloop()

    def close(self):
        self.visible = False
        try:
            self.root.destroy()
        except TclError:
            pass
        self.on_close_handler("raw_window")
