import json, os


class Device:
    """
    A model for handling all of our configuration data.
    This way we can have multiple states of configs, and we can work around the different stages.
    """
    def __init__(self, name, port, baud, switch_g, gy91_config, lis_config):
        """
        Parameters:
            name: str
                Human readable name of the device
            port: str
                The serial port
            baud: int
                Baud rate for the communication (basically the speed)
            switch_g: float
                The g value where we switch between gy91 and lis
            gy91_config:
            lis_config: dict
                Configuration data for each of our accelerometer.
                They have a "scale" and a "bias" float in them.
        """
        self.name = name
        self.port = port
        self.baud = baud
        self.switch_g = switch_g
        self.gy91 = gy91_config
        self.lis = lis_config

    @staticmethod
    def get_settings_dir():
        """Queries the settings directory (`~/.ksagent`)"""
        directory = os.path.expanduser('~') + "/.ksagent"
        if not os.path.exists(directory):
            os.mkdir(directory)
        return directory

    @staticmethod
    def load_devices():
        """Loads all existing devices."""
        settings_dir = Device.get_settings_dir()
        devices = []
        for file in os.listdir(settings_dir):
            if not file.endswith(".device"):
                continue
            device_json = json.load(open(f"{settings_dir}/{file}", "r"))
            acc_calib = device_json["calibration"]["acc"]
            devices.append(Device(device_json["name"], device_json["port"], device_json["baud"],
                                  acc_calib["switch_g"], acc_calib["gy91"], acc_calib["lis"]))
        return devices

    def save(self):
        """Saves the current setup"""
        device_json = {"name": self.name, "port": self.port, "baud": self.baud, "calibration": {
            "acc": {"switch_g": self.switch_g, "gy91": self.gy91, "lis": self.lis}
        }}
        with open(f"{Device.get_settings_dir()}/{self.name}.device", "w") as settings:
            settings.write(json.dumps(device_json))
            settings.close()
