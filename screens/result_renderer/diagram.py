"""
Place for different diagrams
"""

from matplotlib.axes import Axes
import numpy as np


class Diagram:
    """
    The basic diagram class. Gets two inputs and draws them on a simple plot
    """
    def __init__(self, row: int, column: int, title: str, inputs: list):
        """
        Parameters:
            row:
            column: int
                The diagram's position on the result screen grid
            title: str
                Diagram's title
            inputs: list[str]
                List of input columns
        """
        self.row = row
        self.column = column
        self.title = title
        self.inputs = inputs
        self.data = []

    def draw(self, axes: Axes, row) -> Axes:
        """
        Draws the diagram to a given axis
        Parameters:
            axes: Axes
                The matplotlib diagram to draw on
            row: dict
                The processed packet to draw
        Returns:
            The given axes with the diagram
        """
        self.append_data(row)
        axes.set_title(self.title)
        axes = self.plot(axes)
        return axes

    def plot(self, axes: Axes) -> Axes:
        """
        The actual draw call. Override this if you want something!
        Parameters:
            axes: Axes
                The axes to draw on
        Returns:
            the drawn axes
        """
        axes.plot(self.data[:, 0], self.data[:, 1])
        return axes

    def append_data(self, row):
        """
        The data appender.
        Parameters:
            row: dict
                The packet
        """
        if type(self.data) != np.ndarray:
            self.data = np.array([[row[ci] for ci in self.inputs]])
        else:
            self.data = np.append(self.data, [[row[ci] for ci in self.inputs]], axis=0)

    @staticmethod
    def find_diagram_for_place(diagrams, row, column):
        """
        Finds the diagram for the given coordinates
        Parameters:
            diagrams: list[Diagram]
                All the diagrams to search in.
            row:
            column: int
                The coordinates of the searched diagram
        Returns:
            None or Diagram based on is there a diagram or not
        """
        for di in range(len(diagrams)):
            if diagrams[di] is None:
                continue
            if diagrams[di].row == row and diagrams[di].column == column:
                return di
        return None


class MultiPlotDiagram(Diagram):
    """
    A diagram that is capable of plot more than 1 data into a diagram
    """
    def __init__(self, row, column, title, inputs):
        super().__init__(row, column, title, inputs)

    def plot(self, axes: Axes) -> Axes:
        for ci in range(1, len(self.inputs)):
            axes.plot(self.data[:, 0], self.data[:, ci])
        return axes
