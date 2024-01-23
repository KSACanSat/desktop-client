from matplotlib.axes import Axes


class Diagram:
    def __init__(self, row: int, column: int, title: str, inputs: list):
        self.row = row
        self.column = column
        self.title = title
        self.xdata = []
        self.ydata = []

    def draw(self, axes: Axes, row) -> Axes:
        self.ydata.append(row[1])
        self.xdata.append(row[0])
        axes.set_title(self.title)
        axes.plot(self.xdata, self.ydata)
        return axes

    @staticmethod
    def find_diagram_for_place(diagrams, row, column):
        for di in range(len(diagrams)):
            if diagrams[di] is None:
                continue
            if diagrams[di].row == row and diagrams[di].column == column:
                return di
        return None
