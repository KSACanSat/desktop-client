from tkinter import Tk, TclError


class Screen:
    """
    Egy alaposztály a képernyők deklarálásához.
    """
    def __init__(self, on_close_handler=None):
        """
        :param on_close_handler A leállításkor meghívandó egyéb függvény
        """
        self.visible = False
        self.on_close_handler = on_close_handler
        self.root = Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def start(self):
        self.root.mainloop()
        if not self.visible:
            self.show()

    def show(self):
        """
        Az ablakot megjelenító függvény
        """
        self.visible = True
        self.root.deiconify()

    def hide(self):
        self.visible = False
        self.root.withdraw()

    def close(self):
        """
        Az ablak leállításáért felelős függvény
        """
        self.visible = False
        try:
            self.root.destroy()
        except TclError:
            pass
        if self.on_close_handler is not None:
            self.on_close_handler("raw_window")
