from discalculia.tasks import Task
import math


class PressureAltCalcTask(Task):
    def __init__(self, pressure_label, temperature_label, alt_label):
        self.initial_pressure = None
        self.pressure_label = pressure_label
        self.temperature_label = temperature_label
        self.alt_label = alt_label

    def process(self, data):
        pressure = data[self.pressure_label]
        if self.initial_pressure is None:
            self.initial_pressure = pressure
        alt = -29.2258 * (273 + data[self.temperature_label]) * math.log(pressure / self.initial_pressure)
        data[self.alt_label] = alt
        return data