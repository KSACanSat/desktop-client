from tkinter import Frame, Entry, CENTER, Button, StringVar
from tkinter.ttk import Combobox, Label, Progressbar
from tkinter.messagebox import showerror
from screens.screen import Screen
from serial_comm import SerialManager, UnsupportedProtocolError
from PIL.ImageTk import PhotoImage
from PIL.Image import open
from serial.serialutil import SerialException


class WelcomeScreen(Screen):
    BAUD_OPTIONS = [300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 28800, 31250, 38400, 57600, 115200]

    def __init__(self, root_wnd, connecting_data_setter):
        super().__init__(root_wnd)
        self.connecting_data_setter = connecting_data_setter
        self.root.geometry("500x400")
        self.root.update()
        # Logo part
        self.logo_img = PhotoImage(master=self.root, image=open("assets/logo.png").resize((128, 128)))
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
        self.port_entry.pack(anchor=CENTER)
        # baud rate entry
        self.baud_label = Label(self.form_frame, text="Baud rate:", font=self.prompt_label_font)
        self.baud_label.pack(anchor=CENTER)
        self.baud_entry = Combobox(self.form_frame, font=self.prompt_entry_font)
        self.baud_entry['values'] = WelcomeScreen.BAUD_OPTIONS
        self.baud_entry['state'] = 'readonly'
        self.baud_entry.pack(anchor=CENTER)
        # submit button
        self.submit_button = Button(self.form_frame, text="Csatlakozás", command=self.connect, font=('Arial', 18, 'bold'))
        self.submit_button.pack(anchor=CENTER, pady=10)
        self.form_frame.pack()

    def connect(self):
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
        # pass params
        self.connecting_data_setter(serial_port, int(baud_rate))


class ConnectingScreen(Screen):
    ERRORBOX_TITLE = "KSA Connection Agent: Hiba"

    def __init__(self, root_wnd, on_device_passes):
        super().__init__(root_wnd)
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
        self.data = {"port": port, "baud": baud}
        self.title_text.set(f"Csatlakozás a {self.data['port']} port eszközéhez...")
        self.progressbar.start()
        self.query_device()

    def query_device(self):
        is_error = False
        try:
            if self.serial_conn is None:
                self.serial_conn = SerialManager(self.data['port'], self.data['baud'])
            self.serial_conn.get()
            self.completed_responses += 1
        except SerialException:
            showerror(ConnectingScreen.ERRORBOX_TITLE, "A megadott porton nem található eszköz!")
            is_error = True
        except PermissionError:
            showerror(ConnectingScreen.ERRORBOX_TITLE, "Programozási hiba történt! Nézd meg a konzolt a részletekért!")
            is_error = True
        except UnsupportedProtocolError:
            showerror(ConnectingScreen.ERRORBOX_TITLE, "Az eszköz ismeretlen protokollt használ! Ellenőrizd, hogy jó portot adtál-e meg!")
            is_error = True
        if is_error or self.completed_responses == 5:
            self.progressbar.stop()
            self.hide()
            if not is_error:
                self.on_device_passes(self.serial_conn)
            return
        self.root.after(200, self.query_device)
