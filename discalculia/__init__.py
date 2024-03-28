"""
Source directory for discalucia - our processing engine.

## How to use guide
In order to use the engine you need to set up a `Discalculia` instance and give it the following parameters:
  - Calculation tasks using the `add_task` method. Check them at the Tasks section.
After the setup phase you can give it packets to process using the `process_packet` method and you'll receive the results in your function that you've given to the `on_packet_processed` callback.

## Tasks
In discalculia tasks are the basic steps of the processing flows.
All classes are subclasses of the base `Task` interface which provides abstract definitions for processing. These classes are created before they passed to the `add_task` method and live for the whole runtime.

### Task types
 - `LabelTask` - orders a list of labels to the packet array. It makes easier to identify which data you pass to which task.
 - `CalibrationTask` - takes the whole packet and calibrates the data using the calibration file you provide at startup. More about these files in the tasks documentation.
 - `CalculationTask` - takes labels and calculates the result using the function you provide it at the `process` method.
"""

from discalculia.discalculia import Discalculia
from discalculia.tasks import LabelTask
from discalculia.calc_tasks import PressureAltCalcTask, AccelerationCalibrationTask, AccelerationAltitudeTask #Kalman filter
