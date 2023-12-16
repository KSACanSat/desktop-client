from tkinter import *
from tkinter.ttk import Treeview


class ResultTable(Frame):
    """
    Az eredményeket megjelenítő táblázat
    """
    def __init__(self, parent, columns: list, id_column):
        """
            :parameter parent: A szülő tkinter objektum (ált. az ablak)
            :parameter columns: A táblázat oszlopai `{"id": "Cím"}` formátumban
            :parameter id_column: Az azonosításhoz használt oszlop
        """
        # GENERAL SETUP
        Frame.__init__(self, parent)
        self.id_column = id_column
        self.column_count = len(columns)

        # UI
        #  Görgő és a tábla felállítása
        self.scrollbar = Scrollbar(self)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.table_holder = Treeview(self, yscrollcommand=self.scrollbar.set)
        self.table_holder.pack()
        self.scrollbar.config(command=self.table_holder.yview)

        # A táblázat oszlopainak konfigurációja
        self.table_holder['columns'] = [f"_{column}" for column in columns] # oszlopok hozzáadása
        self.table_holder.column("#0", width=0, stretch=NO)
        self.table_holder.heading("#0", text="", anchor=CENTER)
        for column_id in columns:
            self.table_holder.column(f"_{column_id}", width=80)
            self.table_holder.heading(f"_{column_id}", text=column_id)

    def add_data(self, row: list):
        """
            A táblázat adatainak feltöltője
            :parameter row: A feltöltendő új sor listaként
        """
        self.table_holder.insert(parent='', index=0, iid=row[0], text='',
                                 values=["error" if i >= len(row) else row[i] if row[i] != -1 else "error" for i in range(self.column_count)])
        self.table_holder.pack()
