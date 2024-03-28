from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from screens.screen import Screen
from screens.result_renderer.diagram import Diagram


class ResultScreen(Screen):
    """
    The diagram renderer screen
    """
    def __init__(self, root, rows, columns, size_modifiers=(3.5, 2)):
        """
        Parameters:
            root: Tk
                the root window
            rows:
            columns: int
                Defines the shape of the diagram table
            size_modifiers: tuple of two int, optional
                Modifies the window (and diagram) shape
        """
        super().__init__(root, "Results")
        self.shape = (rows, columns)
        self.figure = Figure(figsize=(columns * size_modifiers[0], rows * size_modifiers[1]), dpi=100)
        self.diagrams = []
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

    def add_diagram(self, diagram):
        """
        Adds a new diagram to the stack
        Parameters:
            diagram: Diagram
                The diagram to add
        """
        self.diagrams.append(diagram)

    def add_result(self, result):
        """
        Adds a new processed packet to the stack
        Parameters:
            result: dict
                A processed packet to add
        """
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
