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


class DataConversionTask(Task):
    """
    A task for divide labels by the set amount
    """
    def __init__(self, label_list):
        """
        Parameters:
            label_list: list of tuples
                The first element of the tuple should be string (the label)
                and the second should be int (the conversion rate).
        """
        self.label_list = label_list

    def process(self, data):
        for label_data in self.label_list:
            data[label_data[0]] = data[label_data[0]] / label_data[1]
            if data[label_data[0]] == 0:
                data[label_data[0]] = None
        return data
