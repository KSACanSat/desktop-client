from tkinter import Frame, constants, CENTER, Button, StringVar, filedialog, Canvas, Entry
from tkinter.ttk import Label, Progressbar, Treeview, Scrollbar
from tkinter.messagebox import showerror
from screens.screen import Screen, MenuItem
from serial_comm import SerialStream, UnsupportedProtocolError
from PIL.ImageTk import PhotoImage
from PIL import Image
from serial.serialutil import SerialException
from device import Device

"""
Az indítóképernyőhöz tartozó ablakok...
"""


class DeviceItem(Frame):
    def __init__(self, master, device, connect_cl, file_cl, more_cl, delete_cl, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.photos = []
        self.device = device
        self.logo = self.__photo("assets/logo.png", (64, 64))
        self.logo.grid(row=0, column=0)
        self.info_frame = Frame(self, width=250)
        self.name = StringVar(master=self)
        self.name_label = Label(self.info_frame, textvariable=self.name)
        self.name_label.pack()
        self.path = StringVar(master=self)
        self.path_label = Label(self.info_frame, textvariable=self.path)
        self.path_label.pack()
        self.info_frame.grid(row=0, column=1)
        self.action_frame = Frame(self, width=128)
        self.connect_btn = self.__action_button(self.action_frame, "assets/connect.png", connect_cl)
        self.connect_btn.grid(row=0, column=0)
        self.load_btn = self.__action_button(self.action_frame, "assets/load.png", file_cl)
        self.load_btn.grid(row=0, column=1)
        self.more_btn = self.__action_button(self.action_frame, "assets/menu.png", more_cl)
        self.more_btn.grid(row=1, column=0)
        self.del_btn = self.__action_button(self.action_frame, "assets/delete.png", delete_cl)
        self.del_btn.grid(row=1, column=1)
        self.action_frame.grid(row=0, column=2)
        self.update_device(device)

    def __action_button(self, master, icon_path, command):
        btn = self.__photo(icon_path, (32, 32), "button", master)
        btn.bind("<Button-1>", lambda _: command(self.device))
        return btn

    def __photo(self, path, size, type="label", master=None):
        parent = master if master is not None else self
        photo = PhotoImage(image=Image.open(path).resize(size), master=parent)
        self.photos.append(photo)
        if type == "button":
            return Button(parent, image=photo)
        else:
            return Label(parent, image=photo, width=8)

    def update_device(self, device):
        self.device = device
        self.name.set(device.name)
        self.path.set(f"{device.port} at speed {device.baud}")


class EditableLabel(Frame):
    def __init__(self, master, label, value, on_change, is_label=True, identifier_data: dict = None):
        super().__init__(master)
        self.on_change = on_change
        self.value = value if not value else "None"
        self.id_dict = identifier_data if identifier_data else {}

        if is_label:
            self.label = Label(self, text=label)
            self.label.pack()

        self.value_label = Label(self, text=self.value)
        self.value_label.pack()
        self.entry = Entry(self)
        self.entry.insert(constants.INSERT, self.value)

        self.value_label.bind("<Button-1>", self.__on_click)
        self.entry.bind("<Button-1>", lambda event: self.entry.focus_set())
        self.entry.bind("<Escape>", self.__on_escape)
        self.entry.bind("<FocusOut>", self.__on_escape)
        self.entry.bind("<Return>", self.__on_return)

    def __on_click(self, _):
        """
        Activate the entry
        """
        self.value_label.pack_forget()
        self.entry.pack()
        self.entry.focus_set()

    def __on_escape(self, _):
        """
        Reset to label if we need to cancel
        """
        self.entry.pack_forget()
        self.entry.delete(0, constants.END)
        self.entry.insert(constants.INSERT, self.value)
        self.value_label.pack()

    def __on_return(self, _):
        """
        Reset to label, but updating its value to the new one (and call the change callback)
        """
        new_text = self.entry.get()
        if new_text == "None":
            return
        self.value = new_text
        self.on_change(new_text, self.id_dict)
        self.entry.pack_forget()
        self.value_label.pack()
        self.value_label.configure(text=new_text)

    def set_value(self, val):
        """
        Sets the UI to the given text value
        Parameters
        ----------
        val: str
            The new value for the UI
        """
        self.value = "None" if val == "" else val
        self.value_label.configure(text=self.value)
        self.entry.delete(0, constants.END)
        self.entry.insert(0, self.value)


class MatrixEntryField(Frame):
    def __init__(self, master, label, shape, data, on_change):
        super().__init__(master)
        self.shape = shape
        self.__validate_data(data)
        self.on_change = on_change

        self.label = Label(self, text=label)
        self.label.pack()

        self.entries = []
        self.entry_frame = Frame(self)
        for i in range(shape[0]):
            for j in range(shape[1]):
                entry = EditableLabel(self.entry_frame, "", self.data[i][j],
                                      lambda val, id_data: self._on_entry_received(val, id_data), False,
                                      {"x": i, "y": j})
                entry.grid(row=i, column=j)
                self.entries.append(entry)
        self.entry_frame.pack()

    def __validate_data(self, data):
        if not data:
            self.data = [[0 for __ in range(self.shape[1])] for _ in range(self.shape[0])]
            return
        self.data = data if len(self.shape) == 2 and self.shape[0] > 1 else [data]
        if len(self.data) != self.shape[0] or len(self.data[0]) != self.shape[1]:
            raise ValueError("Your input matrix is different from the shape you've defined!")

    def _on_entry_received(self, value, id_data):
        self.data[id_data["x"]][id_data["y"]] = float(value)
        self.on_change(self.data)

    def set_value(self, data):
        self.__validate_data(data)
        for i in range(len(self.entries)):
            self.entries[i].set_value(self.data[i // self.shape[1]][i % self.shape[1]])


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
        self.assets_to_save = []
        self.connecting_data_setter = connecting_data_setter
        self.devices = Device.load_devices()
        self.current_device = 0
        self.root.geometry("500x400")
        self.root.update()
        #  Menu part
        menu = MenuItem("Device", children=[
            MenuItem("New device", command=self.create_device)
        ])
        self.menubar = menu.generate_menu(self.root)
        self.root.config(menu=self.menubar)
        # Logo part
        logo_img = PhotoImage(image=Image.open("assets/logo.png").resize((128, 128)), master=self.root)
        self.assets_to_save.append(logo_img)
        self.logo = Label(self.root, image=logo_img)
        self.logo.pack(anchor=CENTER)
        self.title = Label(self.root, text="KSAgent", font=('Arial', 25, 'bold'))
        self.title.pack(anchor=CENTER, pady=12)
        # Form part
        self.form_root = Frame(self.root)
        # Device list
        self.device_list_holder = Frame(self.form_root)
        self.canvas = Canvas(self.device_list_holder, borderwidth=0, background="#ffffff", height=250)
        self.device_list_frame = Frame(self.canvas, background="#ffffff")
        vsb = Scrollbar(self.device_list_holder, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=self.device_list_frame, anchor="nw")
        self.device_list_frame.bind("<Configure>", lambda event: self.on_frame_config())
        self.device_items = []
        for di in range(len(self.devices)):
            gui_device = DeviceItem(self.device_list_frame, self.devices[di],
                                    lambda dev: self.connect(dev), lambda dev: self.load_recording(dev),
                                    lambda dev: self.update_inspector(dev), lambda dev: self.delete_device(dev))
            gui_device.grid(row=di, column=0)
            self.device_items.append(gui_device)
        self.device_list_frame.pack()
        self.device_list_holder.grid(row=0, column=0)

        # Device inspector / editor
        self.inspector_frame = Frame(self.form_root)
        self.name_field = EditableLabel(self.inspector_frame, "Name:", self.devices[self.current_device].name,
                                        lambda val, _: self.modify_device_field("name", val))
        self.name_field.pack()
        self.port_field = EditableLabel(self.inspector_frame, "Serial Port:", self.devices[self.current_device].port,
                                        lambda val, _: self.modify_device_field("port", val))
        self.port_field.pack()
        self.baud_field = EditableLabel(self.inspector_frame, "Baud rate:", self.devices[self.current_device].baud,
                                        lambda val, _: self.modify_device_field("baud", val))
        self.baud_field.pack()
        self.mag_bias = MatrixEntryField(self.inspector_frame, "Magneto bias:",
                                         (1, 3), self.devices[self.current_device].mag_bias,
                                         lambda val: self.modify_device_field("mag_bias", val))
        self.mag_bias.pack()
        self.mag_scale = MatrixEntryField(self.inspector_frame, "Magneto scale:",
                                          (3, 3), self.devices[self.current_device].mag_scale,
                                          lambda val: self.modify_device_field("mag_scale", val))
        self.mag_scale.pack()
        self.inspector_frame.grid(row=0, column=1)
        self.form_root.pack()

    def update_inspector(self, device):
        self.current_device = self.devices.index(device)
        self.name_field.set_value(device.name)
        self.port_field.set_value(device.port)
        self.baud_field.set_value(device.baud)
        self.mag_bias.set_value(device.mag_bias)
        self.mag_scale.set_value(device.mag_scale)

    def modify_device_field(self, field, value):
        if field == "name":
            self.__remove_device(self.devices[self.current_device])
        self.devices[self.current_device].__dict__[field] = value
        self.devices[self.current_device].save()
        if field in ["name", "port", "baud"]:
            self.device_items[self.current_device].update_device(self.devices[self.current_device])

    def __remove_device(self, device):
        import os
        device_path = f"{Device.get_settings_dir()}/{device.name}.device"
        if os.path.exists(device_path):
            os.remove(device_path)

    def on_frame_config(self):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def __update_device_list(self):
        for dev_item in self.device_items: dev_item.grid_forget()
        for dii in range(len(self.device_items)):
            self.device_items[dii].grid(row=dii, column=0)
        self.update_inspector(self.devices[0])

    def create_device(self):
        self.devices.insert(0, Device("Unknown Device", "", "", [], []))
        self.device_items.insert(0, DeviceItem(self.device_list_frame, self.devices[0],
                                               lambda dev: self.connect(dev), lambda dev: self.load_recording(dev),
                                               lambda dev: self.update_inspector(dev), lambda dev: self.delete_device(dev)))
        self.__update_device_list()

    def delete_device(self, device):
        self.device_items[self.devices.index(device)].grid_forget()
        del self.device_items[self.devices.index(device)]
        self.devices.remove(device)
        self.__remove_device(device)
        self.__update_device_list()

    def connect(self, device):
        """
        Formats data for app
        """
        # pass params
        self.connecting_data_setter({"type": "serial", "device": device})

    def load_recording(self, device):
        path = filedialog.askopenfilename(defaultextension="*.txt", filetypes=[("Plain Recording", "*.txt")],
                                          title="Open a recording", parent=self.root)
        import os
        if not os.path.isfile(path):
            showerror("Error!", "Bad path! (Not a file)")
            return
        self.connecting_data_setter({"type": "recording", "path": path, "device": device})


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
        self.device = None
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

    def set_data(self, device):
        """
        Receives a device and checks if it is connected
        :param device The serial device object
        """
        self.device = device
        self.title_text.set(f"Csatlakozás a {self.device.port} port eszközéhez...")
        self.progressbar.start()
        self.query_device()

    def query_device(self):
        """
        The connection checker.
        First it initializes the serial connection, then tries to retrieve any kind of data 5 times.
        If this succeeded the program calls the callback stored in `self.on_device_passes` with the working serial connection.
        """
        is_error = False
        try:
            # Inits the serial connection
            if self.serial_conn is None:
                self.serial_conn = SerialStream(self.device)
            # Query for data
            self.serial_conn.get_message()
            self.completed_responses += 1
        except SerialException:
            # Handling serial errors
            showerror(ConnectingScreen.ERRORBOX_TITLE, "A megadott porton nem található eszköz!")
            is_error = True
        except UnsupportedProtocolError:
            # Handling unsupported things
            showerror(ConnectingScreen.ERRORBOX_TITLE,
                      "Az eszköz ismeretlen protokollt használ! Ellenőrizd, hogy jó portot adtál-e meg!")
            is_error = True
        # Error and finish handling
        if is_error or self.completed_responses == 5:
            # Hiding the window
            self.progressbar.stop()
            self.hide()
            # In case of success send over the connection
            if not is_error:
                self.on_device_passes({"stream": self.serial_conn, "device": self.device})
            return  # Stop the test
        self.root.after(200, self.query_device)  # Schedule the next test
