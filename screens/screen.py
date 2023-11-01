from tkinter import TclError, Toplevel


class Screen:
    """
    Egy alaposztály a képernyők deklarálásához.
    """
    def __init__(self, root_window, on_close_handler=None):
        """
        :param on_close_handler A leállításkor meghívandó egyéb függvény
        """
        self.visible = False
        self.on_close_handler = on_close_handler
        self.root = Toplevel(root_window)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def show(self):
        """
        Az ablakot megjelenító függvény
        """
        self.visible = True
        self.root.deiconify()

    def hide(self):
        """
        Elrejti az ablakot...
        """
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
