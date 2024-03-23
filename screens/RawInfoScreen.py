from .result_table import ResultTable
from .screen import Screen, MenuItem
from tkinter import filedialog


class RawInfoScreen(Screen):
    """
    A natúr adatok megjelenítésért felelős osztály
    """
    # noinspection PyMissingConstructor
    def __init__(self, root_wnd, on_close, on_got_path):
        """
        :param on_close Az ablak kilépésekor meghívandó függvény
        """
        super().__init__(root_wnd, "Raw Info", on_close)
        self.on_got_path = on_got_path
        # # GUI SETUP
        # ## Menu
        menu = MenuItem("File", children=[MenuItem("Start recording", command=self.get_path)])
        self.menu = menu.generate_menu(self.root)
        self.root.config(menu=self.menu)
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
        self.menu.entryconfig("File", state="disabled")

    def get_path(self):
        path = filedialog.asksaveasfilename(parent=self.root, filetypes=[("Plain recording", "*.txt")],
                                            title="Save recorded data", defaultextension=".txt")
        self.on_got_path(path)
