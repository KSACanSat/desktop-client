from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure
from screens.screen import Screen
from screens.result_renderer.diagram import Diagram


class ResultScreen(Screen):
    def __init__(self, root, rows, columns, diagrams):
        super().__init__(root, None)
        self.figure = Figure(figsize=(10, 8), dpi=100)
        self.shape = (rows, columns)
        self.diagrams = diagrams
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

    def add_result(self, result):
        self.figure.clear()
        axes = self.figure.subplots(self.shape[0], self.shape[1])
        for ri in range(self.shape[0]):
            for ci in range(self.shape[1]):
                di = Diagram.find_diagram_for_place(self.diagrams, ri, ci)
                if di is not None:
                    axes[ri][ci] = self.diagrams[di].draw(axes[ri][ci], result)
        self.canvas.draw()
        self.canvas.flush_events()
