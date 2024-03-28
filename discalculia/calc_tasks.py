"""
All the calculation tasks.
"""

from discalculia.tasks import Task, LabelTask
import numpy as np
import math


class PressureAltCalcTask(Task):
    """
    Calculates the altitude by the air pressure.
    Labelling the packet using the `LabelTask` is mandatory in order to use this task!
    """
    def __init__(self, pressure_label, temperature_label, alt_label):
        """
        Parameters:
            pressure_label: str
                Label of pressure field
            alt_label: str
                Label for the outputting altitude
        """
        self.initial_pressure = None
        self.pressure_label = pressure_label
        self.temperature_label = temperature_label
        self.alt_label = alt_label

    def process(self, data):
        pressure = data[self.pressure_label]
        temperature = data[self.temperature_label]
        if self.initial_pressure is None:
            self.initial_pressure = pressure
        # -153.8461 * T0 * (1 - 5.268th root of Pi / P0)
        alt = -153.8461 * (273+temperature) * (1 - (pressure / self.initial_pressure) ** (-1/5.268))
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


class calc_magnetoAnglesTask(Task):
    def __init__(self, magnetoX_label, magnetoY_label, magnetoZ_label):
        self.magnetoX = magnetoX_label
        self.magnetoY = magnetoY_label
        self.magnetoz = magnetoZ_label


class KalmanFilterAngleTask(Task):
    def __init__(self, time_label, gyro_labelX, gyro_labelY, gyro_labelZ, magneto_labelX, magneto_labelY,
                 magneto_labelZ, prevAngle_labelX, prevAngle_labelY, prevAngle_labelZ):
        self.time_label = time_label
        self.gyroX = gyro_labelX
        self.gyroY = gyro_labelY
        self.gyroZ = gyro_labelZ

        self.magneto_labelX = magneto_labelX
        self.magneto_labelY = magneto_labelY
        self.magneto_labelZ = magneto_labelZ

        self.angle_labelX = prevAngle_labelX
        self.angle_labelY = prevAngle_labelY
        self.angle_labelZ = prevAngle_labelZ

        self.AngleX = 0
        self.AngleY = 0
        self.AngleZ = 0

        self.estAngleX = 0
        self.estAngleY = 0
        self.estAngleZ = 0

        self.magnetoAngleX = 0
        self.magnetoAngleY = 0
        self.magnetoAngleZ = 0

        self.errorX = 0
        self.errorY = 0
        self.errorZ = 0

        self.magnetoErrorX = 0  # A magnetometer mérésének szórása
        self.magnetoErrorY = 0
        self.magnetoErrorZ = 0

        self.prevAngleX = 0
        self.prevAngleY = 0
        self.prevAngleZ = 0




    def process(self, data):
        #Magnetometer angles
        self.dt = data[self.time_label]

        self.estAngleX = self.AngleX + data[self.gyroX] * self.dt
        self.estAngleY = self.AngleY + data[self.gyroY] * self.dt
        self.estAngleZ = self.AngleZ + data[self.gyroZ] * self.dt

        self.errorX += 4 ** 2 * self.dt ** 2  # A gyroscope mérésének szórása(nem szórásnégyzete) a 4 fok helyett
        self.errorY += 4 ** 2 * self.dt ** 2
        self.errorZ += 4 ** 2 * self.dt ** 2

        KGX = self.errorX / (self.errorX + self.magnetoErrorX ** 2)
        KGY = self.errorY / (self.errorY + self.magnetoErrorY ** 2)
        KGZ = self.errorZ / (self.errorZ + self.magnetoErrorZ ** 2)

        data[self.gyroX] = (self.estAngleX + KGX * (self.magnetoAngleX - self.estAngleX))
        data[self.gyroY] = (self.estAngleY + KGY * (self.magnetoAngleY - self.estAngleY))
        data[self.gyroZ] = (self.estAngleZ + KGZ * (self.magnetoAngleZ - self.estAngleZ))

        self.errorX = (1 - KGX) * self.errorX
        self.errorY = (1 - KGY) * self.errorY
        self.errorZ = (1 - KGZ) * self.errorZ

        return data

