from .result_table import ResultTable
from .screen import Screen


class RawInfoScreen(Screen):
    """
    A natúr adatok megjelenítésért felelős osztály
    """
    # noinspection PyMissingConstructor
    def __init__(self, on_close):
        """
        :param on_close Az ablak kilépésekor meghívandó függvény
        """
        super().__init__(on_close)
        # GUI SETUP
        self.table = ResultTable(self.root, {"time": "Idő", "sensor1": "1. műszer"}, "time")
        self.table.pack()

    def add_row(self, row):
        """
        Sor hozzáadása a táblázathoz
        :param row a hozzáadandó sor
        """
        if self.visible:
            self.table.add_data(row)
