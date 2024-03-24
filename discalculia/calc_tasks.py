"""
All the calculation tasks.
"""

from discalculia.tasks import Task
import math


class PressureAltCalcTask(Task):
    """
    Calculates the altitude by the air pressure.
    Labelling the packet using the `LabelTask` is mandatory in order to use this task!
    """
    def __init__(self, pressure_label, alt_label):
        """
        Parameters:
            pressure_label: str
                Label of pressure field
            alt_label: str
                Label for the outputting altitude
        """
        self.initial_pressure = None
        self.pressure_label = pressure_label
        self.alt_label = alt_label

    def process(self, data):
        pressure = data[self.pressure_label]
        if self.initial_pressure is None:
            self.initial_pressure = pressure
        # -153.8461 * T0 * (1 - 5.268th root of Pi / P0)
        alt = -153.8461 * 288 * (1 - (pressure / self.initial_pressure) ** (-1/5.268))
        data[self.alt_label] = alt
        return data


class AccelerationCalibrationTask(Task):
    """
    Calculates real acceleration from the arduino data.
    Labelling using the `LabelTask` is mandatory in order to use this task!
    """

    def __init__(self, device, acc_labels, sensor):
        """
        Parameters:
            device: Device
                The current configuration
            acc_labels: list[str]
                List of labels where we store nature arduino acceleration
            sensor: str
                Can be "gy-91", "lis" or "combined" (other values will raise and error)
                In the first two cases we'll use the selected sensor's config data everywhere, otherwise
                we switch between gy-91 and lis config data at `device.switch_g`.
        """
        self.device = device
        self.acc_labels = acc_labels
        self.sensor = sensor
        self.__gy91_edge = self.__get_raw_value(7, "gy-91") if self.sensor == "combined" else float("-inf")
        if self.sensor not in ["gy-91", "lis", "combined"]:
            raise ValueError("Sensor can only be gy-91, lis or combined")

    def __get_raw_value(self, real_val, sensor=None):
        sensor = sensor if sensor else self.sensor
        return int((real_val - self.device.__dict__[sensor]["bias"]) / self.device.__dict__[sensor]["scale"])

    def process(self, data):
        for accl in self.acc_labels:
            config = (self.device.lis if data[accl] >= self.__gy91_edge else self.device.gy91) if self.sensor == "combined" else self.device.__dict__[self.sensor]
            data[accl] = config["scale"] * data[accl] + config["bias"]
        return data


class AccelerationAltitudeTask(Task):
    """
    Integrates acceleration to s on the specified axis.
    Requirements: `LabelTask` and some calibration for acceleration
    """

    def __init__(self, time_label, acc_label, acc_alt_label):
        """
        Parameters:
            time_label (str):
                Label for the time field.
            acc_label (str):
                Label for the acceleration (only one axis)
            acc_alt_label (str):
                Label for the outputting altitude
        """
        self.time_label = time_label
        self.acc_label = acc_label
        self.acc_alt_label = acc_alt_label
        self.last_acc = 0

    def process(self, data):
        alt = self.last_acc + 0.5 * data[self.acc_label] * data[self.time_label] ** 2
        self.last_acc = data[self.acc_label]
        data[self.acc_label] = alt
        return data
