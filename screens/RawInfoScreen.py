from .result_table import ResultTable
from .screen import Screen
from tkinter import Menu, filedialog


class RawInfoScreen(Screen):
    """
    A natúr adatok megjelenítésért felelős osztály
    """
    # noinspection PyMissingConstructor
    def __init__(self, root_wnd, on_close, on_got_path):
        """
        :param on_close Az ablak kilépésekor meghívandó függvény
        """
        super().__init__(root_wnd, on_close)
        self.on_got_path = on_got_path
        # # GUI SETUP
        # ## Menu Setup
        self.root.title("Raw Info Screen")
        self.menubar = Menu(self.root)
        self.file_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Start recording", command=self.get_path)
        self.root.config(menu=self.menubar)
        # ## Table Setup
        self.table = ResultTable(self.root, ["Time", "ID", "Gyro X", "Gyro Y", "Gyro Z", "Mag X", "Mag Y", "Mag Z", "Acc X", "Acc Y", "Acc Z","Temp", "Press", "Lat", "Long"], "time")
        self.table.pack()

    def add_row(self, row):
        """
        Sor hozzáadása a táblázathoz
        :param row a hozzáadandó sor
        """
        if self.visible:
            self.table.add_data(row)

    def disable_saving(self):
        self.menubar.entryconfig("File", state="disabled")

    def get_path(self):
        path = filedialog.asksaveasfilename(parent=self.root, filetypes=[("Plain recording", "*.txt")],
                                            title="Save recorded data", defaultextension=".txt")
        self.on_got_path(path)
