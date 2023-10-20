from tkinter import *
from tkinter.ttk import Treeview


class ResultTable(Frame):
    def __init__(self, parent, columns: dict, id_column):
        # GENERAL SETUP
        Frame.__init__(self, parent)
        self._keys = []
        self.columns = columns
        self.id_column = id_column

        # UI
        self.scrollbar = Scrollbar(self)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.table_holder = Treeview(self, yscrollcommand=self.scrollbar.set)
        self.table_holder.pack()
        self.scrollbar.config(command=self.table_holder.yview)

        self.table_holder['columns'] = [f"_{column}" for column in self.columns.keys()]
        self.table_holder.column("#0", width=0, stretch=NO)
        self.table_holder.heading("#0", text="", anchor=CENTER)
        for column_id in self.columns.keys():
            self.table_holder.column(f"_{column_id}", width=80)
            self.table_holder.heading(f"_{column_id}", text=self.columns[column_id])

    def add_data(self, row: dict):
        self.table_holder.insert(parent='', index=0, iid=row[self.id_column], text='', values=[str(c) for c in row.values()])
        self.table_holder.pack()
