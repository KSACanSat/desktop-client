"""
Home of task definitions.
"""

from abc import ABC, abstractmethod


class Task(ABC):
    """
    Base class for tasks.
    It only contains the `process` method which will run on the calculation thread.
    """
    @abstractmethod
    def process(self, data):
        raise NotImplementedError


class LabelTask(Task):
    """
    Simple task for labeling a packet.
    """
    def __init__(self, labels):
        """
        Parameters:
        -----------
        labels: list of strings
            Labels for every bit of the packet.
        """
        self.labels = labels

    def process(self, data):
        labelled_packet = {}
        for label_index in range(len(self.labels)):
            labelled_packet[self.labels[label_index]] = data[label_index]
        return labelled_packet
