from tkinter import Frame, Entry, CENTER, Button
from tkinter.ttk import Combobox, Label
from screens.screen import Screen
from PIL.ImageTk import PhotoImage
from PIL.Image import open


class WelcomeScreen(Screen):
    BAUD_OPTIONS = [300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 28800, 31250, 38400, 57600, 115200]

    def __init__(self):
        super().__init__()
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
        print("Connectiong...")
