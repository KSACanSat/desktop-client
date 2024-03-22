import json, os


class Device:
    """
    A kapcsolat beállításai
    """
    def __init__(self, name, port, baud, mag_bias, mag_scale):
        """
        :param port A soros port
        :param baud A baud rate
        """
        self.name = name
        self.port = port
        self.baud = baud
        self.mag_bias = mag_bias
        self.mag_scale = mag_scale

    @staticmethod
    def get_settings_dir():
        """
        Lekérdezi a beállítások fájlját
        """
        directory = os.path.expanduser('~') + "/.ksagent"
        if not os.path.exists(directory):
            os.mkdir(directory)
        return directory

    @staticmethod
    def load_devices():
        """
        Betölti az aktuális eszközöket
        """
        settings_dir = Device.get_settings_dir()
        devices = []
        for file in os.listdir(settings_dir):
            if not file.endswith(".device"):
                continue
            device_json = json.load(open(f"{settings_dir}/{file}", "r"))
            mag_calibration = device_json["calibration"]["mag"]
            devices.append(Device(device_json["name"], device_json["port"], device_json["baud"],
                                  mag_calibration["bias"], mag_calibration["scale"]))
        return devices

    def save(self):
        """
        Elmenti az akutális beállításokat
        """
        device_json = {"name": self.name, "port": self.port, "baud": self.baud, "calibration": {
            "mag": {"bias": self.mag_bias, "scale": self.mag_scale}
        }}
        with open(f"{Device.get_settings_dir()}/{self.name}.device", "w") as settings:
            settings.write(json.dumps(device_json))
            settings.close()
