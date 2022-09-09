#!/usr/bin/python3
# ----------------------------------------------------------------------
# TomoXRD - TomoXRD Collection GUI Software.
# Author: Christofanis Skordas (skordasc@uchicago.edu)
# Copyright (C) 2022  GSECARS, The University of Chicago
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------

import math
import os.path
import time
import numpy as np
from epics import caget, caput
from typing import Optional
from qtpy.QtCore import QObject, Signal

from tomoxrd.widget.custom import MsgBox


class ScanningModel(QObject):
    # SIGNALS
    status_message_changed: Signal = Signal(str)
    scan_is_running: Signal = Signal(bool)
    frame_number_changed: Signal = Signal(int)
    frame_counter_changed: Signal = Signal(int)
    total_frames_changed: Signal = Signal(int)
    trigger_esperanto_creation: Signal = Signal()
    error_message_changed: Signal = Signal(str)

    # Properties
    _is_running: bool = False
    _aborted: bool = False

    # Detector PVs
    _detector_exposure: str = "13PIL1MCdTe:cam1:AcquireTime"
    _detector_acquire: str = "13PIL1MCdTe:cam1:Acquire"
    _detector_armed: str = "13PIL1MCdTe:cam1:Armed"
    _detector_num_images: str = "13PIL1MCdTe:cam1:NumImages"
    _detector_trigger: str = "13PIL1MCdTe:cam1:TriggerMode"
    _detector_arr_counter: str = "13PIL1MCdTe:cam1:ArrayCounter"
    _detector_file_template: str = "13PIL1MCdTe:cam1:FileTemplate"
    _detector_file_name: str = "13PIL1MCdTe:cam1:FileName"
    _detector_file_number: str = "13PIL1MCdTe:cam1:FileNumber"
    _detector_file_path: str = "13PIL1MCdTe:cam1:FilePath"

    _tiff_file_template: str = "13PIL1MCdTe:TIFF1:FileTemplate"
    _tiff_file_number: str = "13PIL1MCdTe:TIFF1:FileNumber"
    _tiff_file_name: str = "13PIL1MCdTe:TIFF1:FileName"

    _recursive_filter_number = "13PIL1MCdTe:Proc1:NumFilter"
    _recursive_filter_type = "13PIL1MCdTe:Proc1:FilterType"
    _recursive_filter_enable = "13PIL1MCdTe:Proc1:EnableFilter"

    # PSO PVs
    _pso_axis: str = "13BMDPG1:TS:PSOAxisName"
    _pso_command_in: str = "13BMDPG1:TS:PSOCommand.BINP"
    _pso_command_out: str = "13BMDPG1:TS:PSOCommand.BOUT"
    _pso_counts_per_rotation: str = "13BMDPG1:TS:PSOCountsPerRotation"
    _pso_counts_per_step: str = "13BMDPG1:TS:PSOEncoderCountsPerStep"
    _pso_encoder_input: str = "13BMDPG1:TS:PSOEncoderInput"
    _pso_pulse_width: str = "13BMDPG1:TS:PSOPulseWidth"
    _pso_start_taxi: str = "13BMDPG1:TS:PSOStartTaxi"
    _pso_end_taxi: str = "13BMDPG1:TS:PSOEndTaxi"

    _theta: str = "13BMD:m119"
    _theta_stop: str = "13BMDPG1:TS:RotationStop"
    _base_path: str = "T:/dac_user/2022/BMD_2022-3/Tomo"
    _tiff_file_path: str = "13PIL1MCdTe:TIFF1:FilePath"
    _shutter: str = "13BMD:Unidig2Bo10"  # 1: Open, 0: Close

    _start_position: float = None
    _end_position: float = None
    _exposure_time: float = None
    _rotation_step: float = None
    _trigger_mode: int = 0
    _num_angles: int = 1

    # Helper variables
    _wide_scan: bool = False
    _still_scan: bool = False
    _encoder_dir: int = 1
    _motor_dir: int = 1
    _user_direction: int = 1
    _overall_sense: int = None
    _max_speed: float = None
    _motor_speed: float = None
    _accel_dist: float = None
    _cbf_collection: bool = True
    _frame_number: int = 1
    _filename: str = ""
    _filepath: str = ""
    _file_number: int = 1
    _total_frames: int = None
    _previous_detector_filename: str = ""
    _previous_tiff_filename: str = ""
    _previous_detector_filepath: str = ""
    _previous_tiff_filepath: str = ""

    creating_esperanto: bool = False

    def __init__(self) -> None:
        super(ScanningModel, self).__init__()
        self._pso_axis = caget(self._pso_axis, as_string=True)
        self._max_speed = caget(self._theta + ".VMAX")

        # Set init PSO values
        caput(self._pso_command_out, f"UNITSTOCOUNTS({self._pso_axis}, 360.0)", wait=True)
        reply = caget(self._pso_command_in, as_string=True)
        counts_per_rotation = float(reply[1:])
        caput(self._pso_counts_per_rotation, counts_per_rotation)

    @staticmethod
    def create_error_message(msg: str) -> None:
        print(f"[Generic-Error] - {msg}")
        MsgBox(msg=msg)

    def _calculate_encoder_counts(self, modifier: float, delta: float) -> int:
        """
        Computes the encoder counts for wide and step collections.
        Changes the value for the PSOEncoderCountsPerStep PV to the actual encoder counts.
        """
        if not self._wide_scan:
            counts = round(self._rotation_step * modifier)
        else:
            counts = round(delta * modifier)
        caput(self._pso_counts_per_step, counts)
        return counts

    def _calculate_taxi_distance(self) -> int:
        """
        Makes taxi distance an integer number of measurement deltas >= acceleration distance.
        Adds 1/2 of a delta to ensure that we are really up to speed.
        """
        if self._rotation_step > 0:
            if not self._wide_scan:
                distance = math.ceil(self._accel_dist / self._rotation_step + 0.5) * self._rotation_step
            else:
                distance = math.ceil(self._accel_dist + (self._accel_dist * 0.001))
        else:
            if not self._wide_scan:
                distance = math.floor(self._accel_dist / self._rotation_step - 0.5) * self._rotation_step
            else:
                distance = math.ceil(self._accel_dist - (self._accel_dist * 0.001))
        return distance

    def _compute_senses(self) -> None:
        """
        Computes whether this motion will be increasing or decreasing encoder counts.
        user direction, overall sense.
        """
        # Encoder direction compared to dial coordinates
        self._encoder_dir = 1 if caget(self._pso_counts_per_step) > 0 else -1
        # Get motor direction (dial vs. user); convert (0,1) = (pos, neg) to (1, -1)
        self._motor_dir = 1 if caget(self._theta + ".DIR") == 0 else -1
        # Figure out whether motion is in positive or negative direction in user coordinates
        self._user_direction = 1 if self._end_position > self._start_position else -1
        # Figure out overall sense: +1 if motion in + encoder direction, -1 otherwise
        self._overall_sense = self._user_direction * self._motor_dir * self._encoder_dir

    def _compute_pso(self) -> None:
        # Compute the actual delta to keep each interval an integer number of encoder counts
        encoder_multiply = float(caget(self._pso_counts_per_rotation)) / 360.0
        delta = abs(self._end_position - self._start_position)
        encoder_counts = self._calculate_encoder_counts(modifier=encoder_multiply, delta=delta)

        # Change the rotation step
        self._rotation_step = encoder_counts / encoder_multiply

        # Compute the time for each frame
        self._time_per_angle = self._exposure_time + 0.005
        self._motor_speed = np.abs(self._rotation_step / self._time_per_angle)
        motor_accel_time = float(caget(self._theta + ".ACCL"))
        self._accel_dist = motor_accel_time / 2.0 * float(self._motor_speed)

        # Compute the number of angles
        self._num_angles = int(round(delta / self._rotation_step, 0))

        # Set the taxi distance
        taxi_dist = self._calculate_taxi_distance()
        caput(self._pso_start_taxi, self._start_position - taxi_dist * self._user_direction)

        # Calculate the last point
        caput(self._pso_end_taxi, self._end_position)

    def _program_pso(self) -> None:
        """
        Performs programming of PSO output on the Aerotech driver.
        """
        pso_input = int(caget(self._pso_encoder_input, as_string=True))
        # Make sure the PSO control is off
        caput(self._pso_command_out, f"PSOCONTROL {self._pso_axis} RESET", wait=True)
        # Set the output to occur from the I/O terminal on the controller
        caput(self._pso_command_out, f"PSOOUTPUT {self._pso_axis} CONTROL 0 1", wait=True)
        # Set the pulse width.  The total width and active width are the same, since this is a single pulse.
        pulse_width = caget(self._pso_pulse_width)
        caput(self._pso_command_out, f"PSOPULSE {self._pso_axis} TIME {pulse_width},{pulse_width}", wait=True)
        # Set the pulses to only occur in a specific window
        caput(self._pso_command_out, f"PSOOUTPUT {self._pso_axis} PULSE WINDOW MASK", wait=True)
        # Set which encoder we will use.  3 = the MXH (encoder multiplier) input, which is what we generally want
        caput(self._pso_command_out, f"PSOTRACK {self._pso_axis} INPUT {pso_input}", wait=True)
        # Set the distance between pulses. Do this in encoder counts.
        encoder_counts_per_step = int(np.abs(caget(self._pso_counts_per_step)))
        fixed_encoder_counts = 1
        if not self._wide_scan:
            caput(self._pso_command_out, f"PSODISTANCE {self._pso_axis} FIXED {encoder_counts_per_step}", wait=True)
        else:
            # Convert acceleration distance to encoder counts and set as PSODISTANCE fixed
            encoder_multiply = float(caget(self._pso_counts_per_rotation)) / 360.0
            fixed_encoder_counts = int(
                round(math.ceil(self._accel_dist + (self._accel_dist * 0.001)) * encoder_multiply)
            )
            caput(self._pso_command_out, f"PSODISTANCE {self._pso_axis} FIXED {fixed_encoder_counts}", wait=True)

        # Which encoder is being used to calculate whether we are in the window.  1 for single axis
        caput(self._pso_command_out, f"PSOWINDOW {self._pso_axis} 1 INPUT {pso_input}", wait=True)

        # Calculate window function parameters.  Must be in encoder counts, and is
        # referenced from the stage location where we arm the PSO.  We are at that point now.
        # We want pulses to start at start - delta/2, end at end + delta/2.
        if not self._wide_scan:
            range_start = -round(np.abs(encoder_counts_per_step) / 2) * self._overall_sense
            range_length = np.abs(encoder_counts_per_step) * self._num_angles
        else:
            range_start = -fixed_encoder_counts * self._overall_sense
            range_length = np.abs(encoder_counts_per_step) * self._num_angles

        # The start of the PSO window must be < end.  Handle this.
        if self._overall_sense > 0:
            window_start = range_start
            window_end = window_start + range_length
        else:
            window_end = range_start
            window_start = window_end - range_length
        caput(
            self._pso_command_out,
            f"PSOWINDOW {self._pso_axis} 1 RANGE {window_start - 5},{window_end + 5}",
            wait=True
        )

    def _prepare_detector(self) -> None:
        """
        Sets the pre-collection values to the detector PVs
        Trigger mode: #0: Internal, #2: Ext-Trigger, #3: Multi-Trigger
        """
        # Sets the exposure time
        caput(self._detector_exposure, self._exposure_time, wait=True)
        # Sets the number of images
        caput(self._detector_num_images, self._num_angles, wait=True)
        # Resets the image array counter
        caput(self._detector_arr_counter, 0, wait=True)
        # Sets the trigger mode
        caput(self._detector_trigger, self._trigger_mode, wait=True)
        # Sets the file name for the TIFF plugin
        caput(self._tiff_file_name, self._filename)
        # Sets the file name for the detector
        caput(self._detector_file_name, self._filename)
        # Sets the starting file number for the TIFF plugin
        caput(self._tiff_file_number, self._frame_number)

        detector_template = "%s%s_%4.4d_0001.tif"
        tiff_template = "%s%s_%4.4d.tif"
        if not self._still_scan and not self._wide_scan:
            if self._cbf_collection:
                # Set the necessary values for .cbf collection
                detector_template = "%s%s_%4.4d.cbf"
                tiff_template = "%s%s_merged.tif"
                # Save the latest detector file number and set the current as frame number
                self._file_number = caget(self._detector_file_number)
                caput(self._detector_file_number, self._frame_number, wait=True)
                # Sets the detector file path for .cbf collection
                caput(self._detector_file_path, caget(self._tiff_file_path, as_string=True))
                # Set the n filtered
                caput(self._recursive_filter_number, self._num_angles, wait=True)
                # Enable the filter
                caput(self._recursive_filter_enable, 1, wait=True)
                # Set filter to sum
                caput(self._recursive_filter_type, 2, wait=True)

        # Sets the detector file template
        caput(self._detector_file_template, detector_template)
        # Sets the tiff file template
        caput(self._tiff_file_template, tiff_template)

    def _cleanup_pso(self) -> None:
        caput(self._pso_command_out, f"PSOWINDOW {self._pso_axis} 1 OFF", wait=True)
        caput(self._pso_command_out, f"PSOCONTROL {self._pso_axis} OFF", wait=True)

    def _reset_detector(self) -> None:
        """
        Resets the detector's trigger mode and the number of images,
        after the scan is completed/aborted.
        """
        # Resets the number of images
        caput(self._detector_num_images, 1, wait=True)
        # Resets the trigger mode to internal
        caput(self._detector_trigger, 0, wait=True)
        # Resets the extension file template
        if not self._still_scan and not self._wide_scan:
            caput(self._detector_file_template, "%s%s_%4.4d_0001.tif")
            caput(self._tiff_file_template, "%s%s_%4.4d.tif")
            if self._cbf_collection:
                caput(self._recursive_filter_number, 1, wait=True)
                # Reset file number
                caput(self._detector_file_number, self._file_number, wait=True)
        # Reset file path
        caput(self._tiff_file_path, self._previous_tiff_filepath, wait=True)
        caput(self._detector_file_path, self._previous_detector_filepath, wait=True)
        # Reset file name
        caput(self._tiff_file_name, self._previous_tiff_filename, wait=True)
        caput(self._detector_file_name, self._previous_detector_filename, wait=True)

    def _wait_for_collection(self) -> None:
        frame_counter = 0

        while not self._aborted:
            if caget(self._shutter) == 0:
                break

            if not caget(self._detector_armed) == 0:
                # Get the current frame number
                if self._cbf_collection:
                    frame = int(caget(f"{self._detector_arr_counter}_RBV"))
                else:
                    frame = caget(self._tiff_file_number)
                # Update the frame number input box whilst scanning
                if self._frame_number != frame:
                    self._frame_number = frame
                    self.frame_number_changed.emit(self._frame_number)

                    # Update the frame counter
                    frame_counter += 1
                    self.frame_counter_changed.emit(frame_counter)
                continue
            break

        # Close the shutter
        self.toggle_shutter(on=False)

        # Add delay
        time.sleep(0.5)

    def toggle_cbf_collection(self, state: int) -> None:
        self._cbf_collection = state

    def prepare_scan(
            self,
            start: float,
            end: float,
            exposure: float,
            frame: int,
            filename: str,
            filepath: str,
            step: Optional[float] = None,
    ) -> bool:
        self.scan_is_running.emit(True)
        self._is_running = True
        self.status_message_changed.emit("Preparing")
        self._start_position = start
        self._end_position = end
        self._exposure_time = exposure
        self._frame_number = frame
        self._filename = filename
        self._filepath = filepath

        self.creating_esperanto = False

        limited = False

        if start is not None or end is not None:
            # Check theta limits before collection
            low_limit = caget(self._theta + ".LLM")
            high_limit = caget(self._theta + ".HLM")
            taxi_start = caget(self._pso_start_taxi)

            if taxi_start < low_limit or end < low_limit:
                self.error_message_changed.emit(f"You have reached the low limit of the {self._theta}.")
                limited = True
            if taxi_start > high_limit or end > high_limit:
                self._model.error_message_changed.emit(f"You have reached the high limit of the {self._theta}.")
                limited = True

            if step is None:
                self._wide_scan = True
                self._trigger_mode = 2
                next_filepath = self._filepath
            else:
                self._wide_scan = False
                self._rotation_step = step
                self._trigger_mode = 3

                # Update filepath for step sacn
                next_filepath = self._filepath + self._filename

            self._still_scan = False

            self._compute_senses()
            self._compute_pso()
            self._program_pso()
        else:
            self._still_scan = True
            self._wide_scan = False
            self._trigger_mode = 0
            self._num_angles = 1
            next_filepath = self._filepath

        # Check filepath
        if not os.path.exists(next_filepath):
            os.makedirs(next_filepath)

        self._previous_tiff_filepath = caget(self._tiff_file_path)
        self._previous_tiff_filename = caget(self._tiff_file_name)
        self._previous_detector_filepath = caget(self._detector_file_path)
        self._previous_detector_filename = caget(self._detector_file_name)
        caput(self._tiff_file_path, next_filepath.replace(self._base_path, "/DAC"), wait=True)

        self._prepare_detector()

        return limited

    def collect_still(self) -> None:
        # Set the scan status to running
        self.status_message_changed.emit("Scanning")

        self.toggle_shutter(on=True)

        # Arm the detector
        caput(self._detector_acquire, 1)
        time.sleep(0.5)

        self._wait_for_collection()
        self._finish_scan()

    def toggle_shutter(self, on: bool) -> None:
        if on:
            status = 1
        else:
            status = 0

        caput(self._shutter, status, wait=True)

    def collect_projections(self) -> None:
        # Set the scan status to running
        self.status_message_changed.emit("Scanning")
        # Arm the PSO
        caput(self._pso_command_out, f"PSOCONTROL {self._pso_axis} ARM", wait=True)
        time.sleep(0.5)
        # Place the motor at the start position using the max velocity
        caput(self._theta + ".VELO", self._max_speed)
        caput(self._theta + ".VAL", caget(self._pso_start_taxi), wait=True)
        caput(self._theta + ".VELO", self._motor_speed)

        self.toggle_shutter(on=True)

        # Arm the detector
        caput(self._detector_acquire, 1)
        time.sleep(0.5)

        # Start the trajectory
        caput(self._theta + ".VAL", caget(self._pso_end_taxi))

        self._wait_for_collection()
        self._finish_scan()

    def _finish_scan(self) -> None:
        # Reset status values
        self._aborted = False
        if not self._still_scan:
            # Cleanup PSO
            self._cleanup_pso()
            # Set motor speed to max and revert motor position
            caput(self._theta + ".VELO", self._max_speed)
            caput(self._theta + ".VAL", self._start_position)

            # Check theta
            while round(caget(self._theta + ".RBV"), 4) != caget(self._theta + ".VAL"):
                continue

            if not self._wide_scan and self._cbf_collection:
                # Trigger esperanto file creation.
                self.creating_esperanto = True
                self.trigger_esperanto_creation.emit()
                # while self.creating_esperanto:
                #     continue

        # Check detector
        if caget(self._detector_armed) == 1:
            caput(self._detector_acquire, 0, wait=True)

        # Reset detector
        self._reset_detector()
        # Change scan running status
        self.scan_is_running.emit(False)
        self._is_running = False
        # Reset frame counter
        self.frame_counter_changed.emit(0)
        # Set finish scan message
        self.status_message_changed.emit("Finished")

    @property
    def is_running(self) -> bool:
        return self._is_running

    @is_running.setter
    def is_running(self, value: bool) -> None:
        self._is_running = value

    @property
    def aborted(self) -> bool:
        """Returns the aborted status of the collection."""
        return self._aborted

    @aborted.setter
    def aborted(self, value: bool) -> None:
        self.status_message_changed.emit("Aborting")
        self._aborted = value

    @property
    def total_frames(self) -> int:
        return self._total_frames

    @total_frames.setter
    def total_frames(self, value: int) -> None:
        self._total_frames = value
        self.total_frames_changed.emit(self._total_frames)
