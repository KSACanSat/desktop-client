from tkinter import Frame, Entry, CENTER, Button, StringVar, filedialog, Menu
from tkinter.ttk import Combobox, Label, Progressbar
from tkinter.messagebox import showerror
from screens.screen import Screen
from serial_comm import SerialStream, UnsupportedProtocolError
from PIL.ImageTk import PhotoImage
from PIL import Image
from serial.serialutil import SerialException
import os
import json

"""
Az indítóképernyőhöz tartozó ablakok...
"""


class ConnectionSettings:
    """
    A kapcsolat beállításai
    """
    def __init__(self, port, baud):
        """
        :param port A soros port
        :param baud A baud rate
        """
        self.port = port
        self.baud = baud

    @staticmethod
    def _get_settings_path():
        """
        Lekérdezi a beállítások fájlját
        """
        directory = os.path.expanduser('~') + "/.ksagent"
        if not os.path.exists(directory):
            os.mkdir(directory)
        return f"{directory}/settings.json"

    @staticmethod
    def load():
        """
        Betölti az aktuális beállításokat
        """
        settings_path = ConnectionSettings._get_settings_path()
        if not os.path.exists(settings_path):
            return ConnectionSettings(None, None)
        settings = json.load(open(settings_path, "r"))
        return ConnectionSettings(settings["port"], settings["baud"])

    def save(self):
        """
        Elmenti az akutális beállításokat
        """
        with open(ConnectionSettings._get_settings_path(), "w") as settings:
            settings.write(json.dumps({"port": self.port, "baud": self.baud}))
            settings.close()


class WelcomeScreen(Screen):
    """
    Az indító űrlap
    """

    BAUD_OPTIONS = [300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 28800, 31250, 38400, 57600, 115200]

    def __init__(self, root_wnd, connecting_data_setter, on_close):
        """
        :param root_wnd A szülő ablak
        :param connecting_data_setter Az űrlap feldolgozásának végén meghívandó függvény, mely továbbítja az adatokat
        """
        super().__init__(root_wnd, "KSAgent Start", on_close)
        self.connecting_data_setter = connecting_data_setter
        self.settings = ConnectionSettings.load()
        self.root.geometry("500x400")
        self.root.update()
        #  Menu part
        self.menubar = Menu(self.root)
        self.file_menu = Menu(self.menubar)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open recording", command=self.load_recording)
        self.root.config(menu=self.menubar)
        # Logo part
        self.logo_img = PhotoImage(master=self.root, image=Image.open("assets/logo.png").resize((128, 128)))
        self.logo = Label(self.root, image=self.logo_img)
        self.logo.pack(anchor=CENTER)
        self.title = Label(self.root, text="KSAgent", font=('Arial', 25, 'bold'))
        self.title.pack(anchor=CENTER, pady=12)

        # Form part
        self.prompt_label_font = ('Arial', 20, 'bold')
        self.prompt_entry_font = ('Arial', 16)
        self.form_frame = Frame(self.root)
        # serial port entry
        self.port_label = Label(self.form_frame, text="Soros port:", font=self.prompt_label_font)
        self.port_label.pack(anchor=CENTER)
        self.port_entry = Entry(self.form_frame, font=self.prompt_entry_font, justify='center')
        if self.settings.port is not None:
            self.port_entry.insert(0, str(self.settings.port))
        self.port_entry.pack(anchor=CENTER)
        # baud rate entry
        self.baud_label = Label(self.form_frame, text="Baud rate:", font=self.prompt_label_font)
        self.baud_label.pack(anchor=CENTER)
        self.baud_entry = Combobox(self.form_frame, font=self.prompt_entry_font)
        self.baud_entry['values'] = WelcomeScreen.BAUD_OPTIONS
        self.baud_entry['state'] = 'readonly'
        if self.settings.baud is not None:
            self.baud_entry.set(str(self.settings.baud))
        self.baud_entry.pack(anchor=CENTER)
        # submit button
        self.submit_button = Button(self.form_frame, text="Csatlakozás", command=self.connect, font=('Arial', 18, 'bold'))
        self.submit_button.pack(anchor=CENTER, pady=10)
        self.form_frame.pack()

    def connect(self):
        """
        Ellenőrzi a beküldött adatok helyességét, elmenti és tuvábbküldi azokat
        """
        # get connection params
        serial_port = self.port_entry.get()
        baud_rate = self.baud_entry.get()
        # null check
        is_error = False
        if serial_port is None or serial_port == "":
            showerror("Csatlakozás", "Nem adtad meg a soros portot!")
            is_error = True
        if baud_rate is None or baud_rate == "":
            showerror("Csatlakozás", "Nem adtad meg a baud ratet!")
            is_error = True
        if is_error:
            return
        # save settings
        self.settings.port = serial_port
        self.settings.baud = baud_rate
        self.settings.save()
        # pass params
        self.connecting_data_setter({"type": "serial", "data": (serial_port, int(baud_rate))})

    def load_recording(self):
        path = filedialog.askopenfilename(defaultextension="*.txt", filetypes=[("Plain Recording", "*.txt")],
                                          title="Open a recording", parent=self.root)
        self.connecting_data_setter({"type": "recording", "data": (path)})


class ConnectingScreen(Screen):
    """
    A kapcsolat ellenőrzéséért felelős ablak.
    """

    ERRORBOX_TITLE = "KSA Connection Agent: Hiba"

    def __init__(self, root_wnd, on_device_passes):
        """
        :param root_wnd A szülő ablak
        :param on_device_passes Az ellenőrzésen átment kapcsolatot fogadó függvény
        """
        super().__init__(root_wnd, "Connecting...")
        self.data = {}
        self.serial_conn = None
        self.completed_responses = 0
        self.on_device_passes = on_device_passes
        # UI INIT
        self.root.geometry("200x50")
        self.title_text = StringVar(self.root, "")
        self.title = Label(self.root, textvariable=self.title_text)
        self.title.pack(anchor=CENTER)
        self.progressbar = Progressbar(self.root, orient="horizontal", mode="indeterminate", length=180)
        self.progressbar.pack(anchor=CENTER, pady=10)

    def set_data(self, port, baud):
        """
        Fogadja a tesztelendó kapcsolat adatait és elindítja az ellenőrzést.
        :param port A soros port
        :param baud A baud rate
        """
        self.data = {"port": port, "baud": baud}
        self.title_text.set(f"Csatlakozás a {self.data['port']} port eszközéhez...")
        self.progressbar.start()
        self.query_device()

    def query_device(self):
        """
        Az kapcsolatot ellenőrző függvény.
        Először is inicializálja a soros kapcsolatot, majd 5 egymást követő alkalommal megpróbál adatot lekérni az eszköztől.
        Ha ez sikerült, a program elküldi a `self.on_device_passes` callbackben meghatárzott függvénynek a kapcsolatot.
        """
        is_error = False
        try:
            # Kapcsolat inicializációja, ha még nincs meg
            if self.serial_conn is None:
                self.serial_conn = SerialStream(self.data['port'], self.data['baud'])
            # Adat lekérdezése
            self.serial_conn.get_message()
            self.completed_responses += 1
        except SerialException:
            # A soros kapcsolatban létrejött hiba kezelése
            showerror(ConnectingScreen.ERRORBOX_TITLE, "A megadott porton nem található eszköz!")
            is_error = True
        except UnsupportedProtocolError:
            # Nem támogatott eszköz kezelése
            showerror(ConnectingScreen.ERRORBOX_TITLE, "Az eszköz ismeretlen protokollt használ! Ellenőrizd, hogy jó portot adtál-e meg!")
            is_error = True
        # A hibák, illetve a teszt végének kezelése
        if is_error or self.completed_responses == 5:
            # Ablak elrejtése
            self.progressbar.stop()
            self.hide()
            # Siker esetén a program továbbküldése
            if not is_error:
                self.on_device_passes(self.serial_conn)
            return  # Annak megakadályozása, hogy a teszt tovább fusson
        self.root.after(200, self.query_device)  # A következő teszt ütemezése
