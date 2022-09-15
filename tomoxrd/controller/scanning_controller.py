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
import datetime
import threading
import time
import numpy as np
from qtpy.QtCore import QObject, Signal
from epics import caget, caput
from typing import Optional

from tomoxrd.model import MainModel
from tomoxrd.controller import FilenameController
from tomoxrd.widget import MainWidget


class ScanningController(QObject):
    current_collection_changed: Signal = Signal(int)
    estimated_time_changed: Signal = Signal(float)

    tomo_x = -127.0
    tomo_z = 50.0
    xrd_x = 95.0
    xrd_z = 0.0
    detector_out = 100.0

    _horizontal_motor: str = "13BMD:m123"
    _vertical_motor: str = "13BMD:m115"
    _focus_motor: str = "13BMD:m122"
    _shutter: str = "13BMD:Unidig2Bo10"  # 1: Open, 0: Close

    _previous_horiz_pos: float = None
    _previous_vert_pos: float = None
    _previous_focus_pos: float = None
    _total_collections: int = 1
    _current_collection: int = 1

    _multiple_collection_aborted: bool = False
    _multiple_collection_running: bool = False
    _at_xrd_position: bool = False
    _current_row: int = 0
    _start_time: datetime.datetime

    def __init__(self, model: MainModel, widget: MainWidget, controller: FilenameController) -> None:
        super(ScanningController, self).__init__()

        self._model = model
        self._widget = widget
        self._controller = controller

        self._connect_methods()
        self._update_total_frames()
        self._update_estimated_time()

    def _connect_methods(self) -> None:
        self.current_collection_changed.connect(self._update_current_collection)
        self._model.scanning.status_message_changed.connect(self._widget.collection_status.update_status_message)
        self._model.scanning.scan_is_running.connect(self._widget.collection_status.toggle_collect_abort_button)
        self._model.scanning.scan_is_running.connect(self._disable_gui_while_collecting)
        self._model.scanning.trigger_esperanto_creation.connect(self._create_esperanto_files)
        self._widget.collection_status.btn_collect_abort.clicked.connect(self._collect_abort_btn)
        self._model.scanning.frame_number_changed.connect(self._widget.filename_settings.update_frame_number)
        self._model.scanning.total_frames_changed.connect(self._update_status_total_frames)
        self._model.scanning.frame_counter_changed.connect(self._update_status_current_frames)
        self._widget.collection_settings.combo_collection_type.currentIndexChanged.connect(
            lambda: self._update_total_frames()
        )
        self._widget.collection_settings.spin_step_size.valueChanged.connect(
            lambda: self._update_total_frames()
        )
        self._widget.collection_settings.spin_omega_range_start.valueChanged.connect(
            lambda: self._update_total_frames()
        )
        self._widget.collection_settings.spin_omega_range_end.valueChanged.connect(
            lambda: self._update_total_frames()
        )
        self._widget.collection_settings.spin_exposure.valueChanged.connect(
            lambda: self._update_estimated_time()
        )
        self._widget.filename_settings.check_chrysalis.stateChanged.connect(self._model.scanning.toggle_cbf_collection)
        self._widget.collection_points.btn_add.clicked.connect(self._add_collection_point)
        self._widget.collection_points.btn_clear.clicked.connect(lambda: self._update_total_collections(1))
        self._widget.collection_points.btn_add.clicked.connect(lambda: self._update_total_collections(
            self._total_collections + 1
        ))
        self._widget.collection_points.btn_delete.clicked.connect(lambda: self._update_total_collections(
            self._total_collections - 1
        ))
        self._widget.collection_points.btn_check_all.clicked.connect(lambda: self._update_estimated_time)
        self._widget.collection_points.table_points.enabled_checkboxes_changed.connect(self._iterate_collections)
        self.estimated_time_changed.connect(self._widget.collection_status.update_estimated_time_widget)
        self._widget.collection_settings.combo_collection_type.currentIndexChanged.connect(self._toggle_checkbox_status)
        self._model.scanning.error_message_changed.connect(self._model.scanning.create_error_message)

    def shutter_is_open(self) -> bool:
        """Checks if the shutter is open."""
        if caget(self._shutter) == 1:
            return True
        return False

    def _toggle_checkbox_status(self) -> None:
        if self._widget.collection_settings.combo_collection_type.currentText() == "Step":
            self._widget.filename_settings.check_chrysalis.setEnabled(True)
            self._widget.filename_settings.check_auto_reset_frames.setEnabled(True)
        else:
            self._widget.filename_settings.check_chrysalis.setEnabled(False)
            self._widget.filename_settings.check_auto_reset_frames.setEnabled(False)

    def _esperanto_creator(self) -> None:
        filepath = self._widget.filename_settings.ipt_path.text()
        filename = self._widget.filename_settings.ipt_filename.text()

        if self._widget.collection_points.table_points.rowCount() >= 1:
            filename += f"_{self._widget.collection_points.table_points.item(self._current_row, 0).text()}"

        if not self._model.scanning.aborted:
            self._controller.prepare_for_crysalis(
                num_angles=self._model.scanning.total_frames,
                start=self._widget.collection_settings.spin_omega_range_start.value(),
                end=self._widget.collection_settings.spin_omega_range_end.value(),
                step=self._widget.collection_settings.spin_step_size.value(),
                exposure=self._widget.collection_settings.spin_exposure.value()
            )

        if not self._model.scanning.aborted:
            self._controller.create_esperanto_directory(
                filepath=filepath + filename,
                filename=filename
            )

        if not self._model.scanning.aborted:
            self._controller.copy_set_and_ccd_files(
                filepath=filepath + filename,
                filename=filename
            )

        if not self._model.scanning.aborted:
            self._controller.create_crysalis_exp_settings_file(
                filepath=filepath + filename,
                filename=filename
            )

        if not self._model.scanning.aborted:
            self._controller.create_par_file(
                filepath=filepath + filename,
                filename=filename
            )

        if not self._model.scanning.aborted:
            self._controller.convert_to_esperanto(
                filepath=filepath + filename,
                filename=filename,
                num_angles=self._model.scanning.total_frames
            )

        self._model.scanning.creating_esperanto = False

    def _create_esperanto_files(self) -> None:
        esperanto_creator_thread = threading.Thread(target=self._esperanto_creator, args=())

        collection_points = self._widget.collection_points.table_points.rowCount()
        if collection_points < 1:
            esperanto_creator_thread.start()
        else:
            if self._widget.collection_points.table_points.enabled_checkboxes[self._current_row].isChecked():
                esperanto_creator_thread.start()

    def _update_total_collections(self, collections_number: int) -> None:

        if self._widget.collection_points.table_points.rowCount() <= 1:
            self._total_collections = 1
        else:
            self._total_collections = collections_number
        self._widget.collection_status.lbl_collections.setText(f"0/{self._total_collections} Collections")
        self._update_estimated_time()

    def _iterate_collections(self) -> None:
        collection_counter = 0
        for checkbox in self._widget.collection_points.table_points.enabled_checkboxes:
            if checkbox.isChecked():
                collection_counter += 1

        self._update_total_collections(collections_number=collection_counter)

    def _update_current_collection(self, collection_number: int) -> None:
        self._current_collection = collection_number - 1
        self._widget.collection_status.lbl_collections.setText(
            f"{collection_number}/{self._total_collections} Collections"
        )
        self._update_estimated_time()

    def _update_total_frames(self) -> None:
        if self._widget.collection_settings.combo_collection_type.currentText() == "Step":
            start = self._widget.collection_settings.spin_omega_range_start.value()
            end = self._widget.collection_settings.spin_omega_range_end.value()
            step = self._widget.collection_settings.spin_step_size.value()
            self._model.scanning.total_frames = round(np.abs(end - start) / step)
        else:
            self._model.scanning.total_frames = 1

    def _update_status_total_frames(self, frame_number: int) -> None:
        self._widget.collection_status.lbl_frames.setText(f"0/{frame_number} Frames")
        self._update_estimated_time()

    def _update_status_current_frames(self, frame_number: int) -> None:
        if frame_number > self._model.scanning.total_frames:
            frame_number = self._model.scanning.total_frames

        self._widget.collection_status.lbl_frames.setText(f"{frame_number}/{self._model.scanning.total_frames} Frames")

    def disable_gui_while_moving_to_tomo(self, state: bool) -> None:
        self._widget.collection_status.btn_collect_abort.setEnabled(not state)
        self._widget.collection_status.btn_prepare_for_xrd.setEnabled(not state)

    def disable_gui_while_moving_to_xrd(self, state: bool) -> None:
        self._widget.collection_status.btn_collect_abort.setEnabled(not state)
        self._widget.collection_status.btn_prepare_for_tomo.setEnabled(not state)

    def _disable_gui_while_collecting(self, state: bool) -> None:
        self._widget.collection_points.setEnabled(not state)
        self._widget.collection_settings.setEnabled(not state)
        self._widget.filename_settings.setEnabled(not state)
        self._widget.collection_status.btn_prepare_for_tomo.setEnabled(not state)
        self._widget.collection_status.btn_prepare_for_xrd.setEnabled(not state)

        if not state:
            if self._widget.collection_settings.combo_collection_type.currentText() == "Step":
                # Check if auto reset frame is selected
                if self._widget.filename_settings.check_auto_reset_frames.isChecked():
                    self._widget.filename_settings.spin_frame_number.setValue(1)
            else:
                frame = int(caget("13PIL1MCdTe:TIFF1:FileNumber"))
                self._widget.filename_settings.spin_frame_number.setValue(frame)

            if self._widget.collection_points.table_points.rowCount() < 1:
                # Update collections
                self._update_total_collections(1)

    def _collect_abort_btn(self) -> None:
        if self._widget.collection_status.btn_collect_abort.text() == "Collect":

            exposure = self._widget.collection_settings.spin_exposure.value()
            start = self._widget.collection_settings.spin_omega_range_start.value()
            end = self._widget.collection_settings.spin_omega_range_end.value()
            step = self._widget.collection_settings.spin_step_size.value()

            if self._widget.collection_settings.combo_collection_type.currentText() == "Still":
                self.collect(exposure=exposure)
            elif self._widget.collection_settings.combo_collection_type.currentText() == "Wide":
                self.collect(exposure=exposure, start=start, end=end)
            else:
                self.collect(exposure=exposure, start=start, end=end, step=step)
        else:
            self.abort()

    def _add_collection_point(self) -> None:
        x = round(caget(self._horizontal_motor), 4)
        y = round(caget(self._vertical_motor), 4)
        z = round(caget(self._focus_motor), 4)
        self._widget.collection_points.table_points.add_point(x_value=x, y_value=y, z_value=z)
        self._update_estimated_time()

    def _compute_estimated_time(self) -> float:
        exposure = self._widget.collection_settings.spin_exposure.value()
        start = self._widget.collection_settings.spin_omega_range_start.value()
        end = self._widget.collection_settings.spin_omega_range_end.value()
        step = self._widget.collection_settings.spin_step_size.value()

        # TODO: Need to include the delay of epics wait=True usage.
        if self._widget.collection_settings.combo_collection_type.currentText() == "Step":
            time_estimate = round(np.abs(end - start) / step) * exposure
            # Add existing delay for step scans
            time_estimate += 2
        else:
            # Add existing delay for still and wide scans
            time_estimate = exposure
            # Account for time.sleep delay added
            time_estimate += 1.5

        return time_estimate

    def _update_estimated_time(self) -> None:
        collection_points = self._widget.collection_points.table_points.rowCount()
        total_estimate = 0.0

        if collection_points < 1:
            total_estimate = self._compute_estimated_time()
        else:
            for row in range(collection_points):
                if self._widget.collection_points.table_points.enabled_checkboxes[row].isChecked():
                    total_estimate += self._compute_estimated_time()

        self.estimated_time_changed.emit(total_estimate)

    def _compute_elapsed_time(self) -> None:
        while self._model.scanning.is_running or self._multiple_collection_running:
            time.sleep(0.1)
            elapsed_time = (datetime.datetime.now() - self._start_time).total_seconds()
            self._widget.collection_status.update_elapsed_time_widget(seconds=elapsed_time)

    def _on_xrd_position(self) -> bool:
        current_x = self._model.bmd.detector_x.readback
        current_z = self._model.bmd.detector_z.readback

        if current_x == self.xrd_x and current_z == self.xrd_z:
            return True
        return False

    def _step_is_larger_than_range(self) -> bool:
        start = self._widget.collection_settings.spin_omega_range_start.value()
        end = self._widget.collection_settings.spin_omega_range_end.value()
        step = self._widget.collection_settings.spin_step_size.value()
        total_range = abs(end - start)
        if step > total_range:
            return True
        return False

    def collect(
            self,
            exposure: float,
            start: Optional[float] = None,
            end: Optional[float] = None,
            step: Optional[float] = None
    ) -> None:

        if not self._on_xrd_position():
            self._model.scanning.scan_is_running.emit(False)
            self._model.scanning.error_message_changed.emit("First move to XRD position.")
            return None

        if self._step_is_larger_than_range():
            self._model.scanning.scan_is_running.emit(False)
            self._model.scanning.error_message_changed.emit(
                "Step size cannot be greater than the total range of the collection!"
            )
            return None

        # Set initial filenames
        file_name = self._widget.filename_settings.ipt_filename.text()
        caput("13PIL1MCdTe:TIFF1:FileName", file_name, wait=True)
        caput("13PIL1MCdTe:cam1:FileName", file_name, wait=True)
        self._controller.starting_frame = self._widget.filename_settings.spin_frame_number.value()
        # Check if there are collection points listed before starting the collection
        if self._widget.collection_points.table_points.rowCount() < 1:
            self._collect_single_point(exposure=exposure, start=start, end=end, step=step)
        else:
            multiple_points_scan = threading.Thread(target=self._collect_multiple_points, args=(
                exposure, start, end, step))
            if not self._model.scanning.aborted:
                multiple_points_scan.start()

        # Elapsed time thread
        elapsed_time_thread = threading.Thread(target=self._compute_elapsed_time, args=())
        # Start the elapsed time thread
        self._start_time = datetime.datetime.now()
        elapsed_time_thread.start()

    def _collect_single_point(
            self,
            exposure: float,
            start: Optional[float] = None,
            end: Optional[float] = None,
            step: Optional[float] = None
    ) -> None:
        """Starts the step fly scan collection."""
        # Set the starting frame for crysalis
        if self._widget.filename_settings.check_chrysalis.isChecked():
            if self._widget.collection_settings.combo_collection_type.currentText() == "Step":
                self._widget.filename_settings.spin_frame_number.setValue(1)
                self._controller.starting_frame = self._widget.filename_settings.spin_frame_number.value()

        next_frame = self._widget.filename_settings.spin_frame_number.value()
        filename = self._widget.filename_settings.ipt_filename.text()
        filepath = self._widget.filename_settings.ipt_path.text()

        limited = self._model.scanning.prepare_scan(
            start=start, end=end, exposure=exposure, step=step,
            frame=next_frame, filename=filename, filepath=filepath)

        if limited:
            self.abort()
            self._revert_sample_positions(with_x_y_z=False)
            return None

        # Check for still collection
        if start is None or end is None:
            scan = threading.Thread(target=self._model.scanning.collect_still, args=())
        else:
            scan = threading.Thread(target=self._model.scanning.collect_projections, args=())

        if not self._model.scanning.aborted:
            # Update current collection number
            self.current_collection_changed.emit(1)
            scan.start()

    def _collect_multiple_points(
            self,
            exposure: float,
            start: Optional[float] = None,
            end: Optional[float] = None,
            step: Optional[float] = None
    ) -> None:
        self._multiple_collection_aborted = False
        self._multiple_collection_running = True

        self._previous_horiz_pos = caget(self._horizontal_motor + ".RBV")
        self._previous_vert_pos = caget(self._vertical_motor + ".RBV")
        self._previous_focus_pos = caget(self._focus_motor + ".RBV")

        collection_number = 0

        collection_points = self._widget.collection_points.table_points.rowCount()
        for row in range(collection_points):
            # Set current collection point
            self._current_row = row

            if self._multiple_collection_aborted:
                break

            if self._widget.collection_points.table_points.enabled_checkboxes[row].isChecked():

                # Set the starting frame
                if self._widget.filename_settings.check_chrysalis.isChecked():
                    if self._widget.collection_settings.combo_collection_type.currentText() == "Step":
                        self._widget.filename_settings.spin_frame_number.setValue(1)
                        self._controller.starting_frame = self._widget.filename_settings.spin_frame_number.value()

                # Update current collection number
                collection_number += 1
                self.current_collection_changed.emit(collection_number)
                # Scan point
                point_name = self._widget.collection_points.table_points.item(row, 0).text()
                x_text = self._widget.collection_points.table_points.cellWidget(row, 1).text()
                y_text = self._widget.collection_points.table_points.cellWidget(row, 2).text()
                z_text = self._widget.collection_points.table_points.cellWidget(row, 3).text()
                x = float(x_text) if x_text else self._previous_horiz_pos
                y = float(y_text) if y_text else self._previous_vert_pos
                z = float(z_text) if z_text else self._previous_focus_pos

                limit_check = self._move_to_point(x, y, z)
                if not limit_check:
                    break

                next_frame = self._widget.filename_settings.spin_frame_number.value()
                filename = self._widget.filename_settings.ipt_filename.text()
                filename += f"_{point_name}"
                filepath = self._widget.filename_settings.ipt_path.text()

                limited = self._model.scanning.prepare_scan(
                    start=start, end=end, exposure=exposure, step=step,
                    frame=next_frame, filename=filename, filepath=filepath
                )
                if limited:
                    self.abort()
                    break

                # Check for still collection
                if start is None or end is None:
                    self._model.scanning.collect_still()
                else:
                    self._model.scanning.collect_projections()

        time.sleep(0.5)
        self._revert_sample_positions()
        self._multiple_collection_running = False
        # Reset current collection point
        self.current_collection_changed.emit(0)

    def _revert_sample_positions(self, with_x_y_z: Optional[bool] = True) -> None:
        self._model.scanning.scan_is_running.emit(True)
        self._model.scanning.status_message_changed.emit("Moving")
        if with_x_y_z:
            caput(self._horizontal_motor, self._previous_horiz_pos, wait=True)
            caput(self._vertical_motor, self._previous_vert_pos, wait=True)
            caput(self._focus_motor, self._previous_focus_pos, wait=True)
        self._model.scanning.scan_is_running.emit(False)
        self._model.scanning.status_message_changed.emit("Finished")

    def _move_to_point(self, x: Optional[float] = None, y: Optional[float] = None, z: Optional[float] = None) -> bool:
        """Moves the stages to the collection point positions to prepare for the collection."""

        self._model.scanning.scan_is_running.emit(True)
        self._model.scanning.status_message_changed.emit("Moving")

        # Check motor limits
        limit_check_horiz = self._check_limits(self._horizontal_motor, x)
        limit_check_vert = self._check_limits(self._vertical_motor, y)
        limit_check_focus = self._check_limits(self._focus_motor, z)

        if not limit_check_horiz or not limit_check_vert or not limit_check_focus:
            return False

        if x is not None:
            caput(self._horizontal_motor + ".VAL", x, wait=True)
        if y is not None:
            caput(self._vertical_motor + ".VAL", y, wait=True)
        if z is not None:
            caput(self._focus_motor + ".VAL", z, wait=True)

        return True

    def _check_limits(self, pv: str, value: float | None) -> bool:
        """
        Checks for high and low limits for a PV.
        :return: False if exceeds the limits, else True
        """
        if value is None:
            return True
        if value < caget(pv + ".LLM"):
            self._model.scanning.error_message_changed.emit(f"You have reached the low limit of the {pv}.")
            return False
        if value > caget(pv + ".HLM"):
            self._model.scanning.error_message_changed.emit(f"You have reached the high limit of the {pv}.")
            return False
        return True

    def abort(self) -> None:
        self._model.scanning.aborted = True
        self._multiple_collection_aborted = True
        self._multiple_collection_running = False
