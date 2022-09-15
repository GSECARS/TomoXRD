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

import threading
import time
from epics import caput
from qtpy.QtCore import QObject, Signal

from tomoxrd.model import MainModel
from tomoxrd.widget import MainWidget
from tomoxrd.controller import ScanningController


class CollectionStatusController(QObject):
    _moving_to_tomo: Signal = Signal(bool)
    _moving_to_xrd: Signal = Signal(bool)

    _tomo_thread_is_running: bool = False
    _xrd_thread_is_running: bool = False
    _move_tomo_aborted: bool = False
    _move_xrd_aborted: bool = False

    def __init__(self, model: MainModel, widget: MainWidget, controller: ScanningController) -> None:
        super(CollectionStatusController, self).__init__()

        self._model = model
        self._widget = widget
        self._controller = controller

        self._connect_collection_status_widgets()

    def _connect_collection_status_widgets(self) -> None:
        self._widget.collection_status.btn_prepare_for_tomo.clicked.connect(self._toggle_tomo_clicked)
        self._widget.collection_status.btn_prepare_for_xrd.clicked.connect(self._toggle_xrd_clicked)

        self._moving_to_tomo.connect(self._widget.collection_status.toggle_tomo_abort_button)
        self._moving_to_xrd.connect(self._widget.collection_status.toggle_xrd_abort_button)
        self._moving_to_tomo.connect(self._controller.disable_gui_while_moving_to_tomo)
        self._moving_to_xrd.connect(self._controller.disable_gui_while_moving_to_xrd)

    def _toggle_tomo_clicked(self) -> None:
        if self._widget.collection_status.btn_prepare_for_tomo.text() == "Abort":
            # Set the status message
            self._widget.collection_status.update_status_message("Aborting")
            # Stop the movement.
            self._move_tomo_aborted = True
            caput("13BMD_TOMO_XPS:allstop", 1)
            caput("13BMD:allstop.VAL", 1)
        else:
            tomo_thread = threading.Thread(target=self._move_to_tomo_position, args=())

            if not self._tomo_thread_is_running:
                if self._move_tomo_aborted:
                    return None
                self._moving_to_tomo.emit(True)
                tomo_thread.start()

    def _move_to_tomo_position(self) -> None:
        # Set the status message
        self._widget.collection_status.update_status_message("Moving to Tomo")
        # Set tomo thread as running
        self._tomo_thread_is_running = True

        if not self._controller.shutter_is_open():

            # Move the detector out
            if not self._move_tomo_aborted:
                self._model.bmd.detector_z.move(self._controller.detector_out, wait=True, timeout=300.0)

            if self._model.bmd.detector_z.readback == self._controller.detector_out:
                # Move detector_x to the tomo position
                if not self._move_tomo_aborted:
                    self._model.bmd.detector_x.move(self._controller.tomo_x, wait=True, timeout=300.0)
                # Move detector_z to the tomo position
                if not self._move_tomo_aborted:
                    self._model.bmd.detector_z.move(self._controller.tomo_z, wait=True, timeout=300.0)
        else:
            self._model.scanning.error_message_changed.emit("Can't move to tomo when the shutter is open!!!")

        # Add delay to account for users spamming the Abort button.
        time.sleep(2.0)
        # Reset tomo thread running status
        self._moving_to_tomo.emit(False)
        self._tomo_thread_is_running = False
        self._move_tomo_aborted = False
        # Set the status message
        self._widget.collection_status.update_status_message("Idle")

    def _toggle_xrd_clicked(self) -> None:
        button = self._widget.collection_status.btn_prepare_for_xrd
        if button.text() == "Abort":
            # Set the status message
            self._widget.collection_status.update_status_message("Aborting")
            # Stop the movement.
            self._move_xrd_aborted = True
            caput("13BMD_TOMO_XPS:allstop", 1)
            caput("13BMD:allstop.VAL", 1)
        else:
            xrd_thread = threading.Thread(target=self._move_to_xrd_position, args=())

            if not self._xrd_thread_is_running:
                if self._move_xrd_aborted:
                    return None
                self._moving_to_xrd.emit(True)
                xrd_thread.start()

    def _move_to_xrd_position(self) -> None:
        # Set the status message
        self._widget.collection_status.update_status_message("Moving to XRD")
        # Set XRD thread as running
        self._xrd_thread_is_running = True

        if not self._controller.shutter_is_open():
            # Move the detector out
            if not self._move_tomo_aborted:
                self._model.bmd.detector_z.move(self._controller.detector_out, wait=True, timeout=300.0)

            if self._model.bmd.detector_z.readback == self._controller.detector_out:
                # Move detector_x to the XRD position
                if not self._move_xrd_aborted:
                    self._model.bmd.detector_x.move(self._controller.xrd_x, wait=True, timeout=300.0)
                # Move detector_z to the XRD position
                if not self._move_xrd_aborted:
                    self._model.bmd.detector_z.move(self._controller.xrd_z, wait=True, timeout=300.0)
        else:
            self._model.scanning.error_message_changed.emit("Can't move to XRD when the shutter is open!!!")

        # Add delay to account for users spamming the Abort button.
        time.sleep(2.0)
        # Reset XRD thread running status
        self._moving_to_xrd.emit(False)
        self._xrd_thread_is_running = False
        self._move_xrd_aborted = False
        # Set the status message
        self._widget.collection_status.update_status_message("Idle")

    def update_collection_status(self) -> None:
        # detector x
        if self._model.bmd.detector_x.moving:
            self._model.bmd.detector_x.moving = False

        # detector z
        if self._model.bmd.detector_z.moving:
            self._model.bmd.detector_z.moving = False
