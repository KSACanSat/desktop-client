from .result_table import ResultTable
from .screen import Screen


class RawInfoScreen(Screen):
    """
    A natúr adatok megjelenítésért felelős osztály
    """
    # noinspection PyMissingConstructor
    def __init__(self, root_wnd, on_close):
        """
        :param on_close Az ablak kilépésekor meghívandó függvény
        """
        super().__init__(root_wnd, on_close)
        # GUI SETUP
        self.table = ResultTable(self.root, ["Idő", "Hőmérséklet", "Légnyomás", "Latitude", "Longitude", "Mes. altitude"], "time")
        self.table.pack()

    def add_row(self, row):
        """
        Sor hozzáadása a táblázathoz
        :param row a hozzáadandó sor
        """
        if self.visible:
            self.table.add_data(row)
