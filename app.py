from serial_comm import SerialStream
from io_manager import *
from screens import *
from tkinter import Tk, TclError
from screens.result_renderer.diagram import *
from discalculia import *


class App(object):
    """
    The main instance of KSAgent.
    For access call `get_instance`!
    """
    _instance = None

    @classmethod
    def get_instance(cls):
        """
        Returns:
            The instance of the application.
        """
        if cls._instance is None:
            cls._instance = App()
        return cls._instance

    def __init__(self):
        self.io = IOManager()
        self.last_time = 0
        # UI setup
        self.schedule_window = Tk()
        self.welcome_window = WelcomeScreen(self.schedule_window, self.connection_data_handler, self.stop)
        self.connect_window = ConnectingScreen(self.schedule_window, self.stream_setter)
        self.raw_window = RawInfoScreen(self.schedule_window, self.stop, self.set_path)
        self.result = ResultScreen(self.schedule_window, 3, 2,(4, 2))
        self.discalculia = Discalculia()
        self.gps = GPSScreen(self.schedule_window)

    def connection_data_handler(self, stream, device):
        """
        Handles the result of `WelcomeScreen`
        Parameters:
            device: Device
                The configuration object which will be used further
            stream: Stream
                A subclass of stream which will provide data for us
        """
        if stream.get_type == "serial":
            # Live
            self.connect_window.set_data(stream, device)
            self.connect_window.show()
            self.raw_window.update_table_columns(["Counter", "Delta Time", "Acc X", "Acc Y",
                                                  "Acc Z", "Temp", "Press", "Lat", "Lng", "GPS Alt", "RSSI"])
            self.result.add_diagram(MultiPlotDiagram(0, 0, "Acceleration", ["time", "acc_x", "acc_y", "acc_z"]))
            self.result.add_diagram(Diagram(0, 1, "Altitude", ["time", "press_alt"]))
            self.result.add_diagram(Diagram(1, 1, "GPS Altitude", ["time", "gps_alt"]))
            self.result.add_diagram(Diagram(2, 1, "Acc Altitude", ["time", "acc_alt"]))
            self.result.add_diagram(Diagram(1, 0, "Temperature", ["time", "temp"]))
            self.result.add_diagram(Diagram(2, 0, "Pressure", ["time", "press"]))
            self.discalculia.add_task(LabelTask(
                ["id", "dt", "acc_x", "acc_y", "acc_z", "temp", "press", "lat", "lng", "gps_alt", "rssi"]))
            self.discalculia.add_task(ActualTimeCalcTask("dt", "time"))
            self.discalculia.add_task(DataConversionTask([("temp", 100), ("lat", 10000), ("lng", 10000)]))
            self.discalculia.add_task(AccelerationCalibrationTask(device, ["acc_x", "acc_y", "acc_z"], "combined"))
            self.discalculia.add_task(PressureAltCalcTask("press", "temp" ,"press_alt"))
            self.discalculia.add_task(AccelerationAltitudeTask("dt", "acc_z", "acc_alt"))
            self.discalculia.add_task(GPSAltFiller("gps_alt"))
        elif stream.get_type == "recording":
            # SD
            self.raw_window.disable_saving()
            self.raw_window.update_table_columns(["Counter", "Timestamp", "GY-91 X", "GY-91 Y", "GY-91 Z", "LIS X", "LIS Y", "LIS Z",
                                                  "mag X", "mag Y", "mag Z", "gyro X", "gyro Y", "gyro Z", "Temp" "Press",
                                                  "Lat", "Lng", "GPS Alt"])
            self.result.add_diagram(MultiPlotDiagram(0, 0, "Acceleration", ["time", "gy91_x", "gy91_y", "gy91_z", "lis_x", "lis_y", "lis_z"]))
            self.result.add_diagram(MultiPlotDiagram(0, 0, "Magnetometer", ["time", "mag_x", "mag_y", "mag_z"]))
            self.result.add_diagram(MultiPlotDiagram(0, 0, "Gyroscope", ["time", "gyro_x", "gyro_y", "gyro_z"]))
            self.result.add_diagram(Diagram(0, 1, "Temperature", ["time", "temp"]))
            self.result.add_diagram(Diagram(1, 1, "Pressure", ["time", "press"]))
            self.result.add_diagram(MultiPlotDiagram(1, 1, "Altitude", ["time", "press_alt"]))
            self.discalculia.add_task(LabelTask(
                ["id", "time", "gy91_x", "gy91_y", "gy91_z", "lis_x", "lis_y", "lis_z",
                 "mag_x", "mag_y", "mag_z", "gyro_x", "gyro_y", "gyro_z", "temp", "press", "lat", "lng", "gps_alt"]))
            self.discalculia.add_task(DataConversionTask([("temp", 100), ("lat", 10000), ("lng", 10000)]))
            self.discalculia.add_task(AccelerationCalibrationTask(device, ["gy91_x", "gy91_y", "gy91_z"], "gy91"))
            self.discalculia.add_task(AccelerationCalibrationTask(device, ["lis_x", "lis_y", "lis_z"], "lis"))
            self.discalculia.add_task(PressureAltCalcTask("press", "press_alt"))
            self.discalculia.add_task(AccelerationAltitudeTask("time", "lis_z", "acc_alt"))
            self.stream_setter(stream, device)

    def stream_setter(self, stream, device):
        """
        Sets the stream for IOManager and inits the "main" setup.
        Parameters:
            stream: Stream
                The data source object
            device: Device
                The configuration object used for further calculations
        """
        self.io.set_stream(stream, device)
        self.welcome_window.hide()
        self.raw_window.show()
        self.result.show()
        self.gps.show()
        self.schedule_window.after(10, self.query_packets)
        self.schedule_window.after(20, self.query_results)

    def set_path(self, path):
        """
        Callback for recording path setting.
        Parameters:
            path: str
                The path of recording. Passed to the IOManager.
        """
        self.io.set_path(path)

    def query_packets(self):
        """
        Handles the nature packets.
        Gets it, shows in the raw result window and schedule it in discalculia
        """
        message = self.io.get_message()
        if message[0] != self.last_time:
            self.raw_window.add_row(message)
            self.discalculia.process_packet(message)
            self.last_time = message[0]
        self.schedule_window.after(20 if self.io.stream.get_type == "serial" else 20, self.query_packets)

    def query_results(self):
        """
        Handles the done discalculia tasks.
        """
        done_packets = self.discalculia.get_done_packets()
        if done_packets is None or done_packets == [None]:
            self.schedule_window.after(20, self.query_results)
            return
        for results in done_packets:
            self.result.add_result(results)
            self.gps.add_result(results)
        self.schedule_window.after(20, self.query_results)

    def show(self):
        """
        Starts the app with the "Welcome" setup.
        """
        self.schedule_window.withdraw()
        self.raw_window.hide()
        self.result.hide()
        self.connect_window.hide()
        self.welcome_window.show()
        self.schedule_window.mainloop()

    def stop(self, close_id):
        """
        Shut-down logic
        """
        try:
            self.schedule_window.destroy()
        except TclError:
            pass
        self.io.stop()
        self.gps.close()
        if close_id != "raw_window":
            self.raw_window.close()
