from tkinter import TclError, Toplevel, Menu


class MenuItem:
    def __init__(self, title, command=None, children=None, enabled=True):
        self.title = title
        self.command = command
        self.children = children
        self.enabled = enabled

    def generate_menu(self, root):
        root_menu = Menu(root)
        if self.children is not None:
            for child in self.children:
                child_menu = child.generate_menu(root_menu)
                print(child_menu, child.title)
                root_menu.add_cascade(menu=child_menu, label=self.title)
        elif self.command is not None:
            root_menu.add_command(label=self.title, command=self.command)
            print(self.title)
        if not self.enabled:
            root_menu.entryconfigure(0, state='disabled')
        return root_menu


class Screen:
    """
    Egy alaposztály a képernyők deklarálásához.
    """
    def __init__(self, root_window, title, on_close_handler=None):
        """
        :param on_close_handler A leállításkor meghívandó egyéb függvény
        """
        self.visible = False
        self.on_close_handler = on_close_handler
        self.root = Toplevel(root_window)
        self.root.title(title)
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
