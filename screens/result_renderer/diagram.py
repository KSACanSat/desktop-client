from matplotlib.axes import Axes
import numpy as np


class Diagram:
    def __init__(self, row: int, column: int, title: str, inputs: list):
        self.row = row
        self.column = column
        self.title = title
        self.inputs = inputs
        self.data = []

    def draw(self, axes: Axes, row) -> Axes:
        self.append_data(row)
        axes.set_title(self.title)
        axes = self.plot(axes)
        return axes

    def plot(self, axes: Axes) -> Axes:
        axes.plot(self.data[:, 0], self.data[:, 1])
        return axes

    def append_data(self, row):
        if type(self.data) != np.ndarray:
            self.data = np.array([[row[ci] for ci in range(len(self.inputs))]])
        else:
            self.data = np.append(self.data, [[row[ci] for ci in range(len(self.inputs))]], axis=0)

    @staticmethod
    def find_diagram_for_place(diagrams, row, column):
        for di in range(len(diagrams)):
            if diagrams[di] is None:
                continue
            if diagrams[di].row == row and diagrams[di].column == column:
                return di
        return None


class MultiPlotDiagram(Diagram):
    def __init__(self, row, column, title, inputs):
        super().__init__(row, column, title, inputs)

    def plot(self, axes: Axes) -> Axes:
        for ci in range(1, len(self.inputs)):
            axes.plot(self.data[:, 0], self.data[:, ci])
        return axes
