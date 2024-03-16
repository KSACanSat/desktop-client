from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from screens.screen import Screen
from screens.result_renderer.diagram import Diagram


class ResultScreen(Screen):
    def __init__(self, root, rows, columns, diagrams, size_modifiers=(3.5, 2)):
        super().__init__(root, None)
        self.shape = (rows, columns)
        self.figure = Figure(figsize=(columns * size_modifiers[0], rows * size_modifiers[1]), dpi=100)
        self.diagrams = diagrams
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

    def add_result(self, result):
        self.figure.clear()
        axes = self.figure.subplots(self.shape[0], self.shape[1], sharex=True)
        for ri in range(self.shape[0]):
            for ci in range(self.shape[1]):
                di = Diagram.find_diagram_for_place(self.diagrams, ri, ci)
                if di is not None:
                    if self.shape[1] > 1:
                        axes[ri][ci] = self.diagrams[di].draw(axes[ri][ci], result)
                    else:
                        axes[ri] = self.diagrams[di].draw(axes[ri], result)
        self.canvas.draw()
        self.canvas.flush_events()

    def close(self):
        self.root.destroy()