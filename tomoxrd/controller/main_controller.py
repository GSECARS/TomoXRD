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

import sys
import time

from win32 import win32gui
from qtpy.QtCore import QSettings, QObject, Signal
from qtpy.QtWidgets import QApplication

from tomoxrd.model import MainModel, QtWorkerModel
from tomoxrd.controller import ScanningController, FilenameController, CollectionStatusController
from tomoxrd.widget import MainWidget


class MainController(QObject):
    """Base controller, initializes sub-controllers, creates and run main app worker and checks for epics connection."""

    _epics_connection_changed: Signal = Signal(bool)

    def __init__(self) -> None:
        super(MainController, self).__init__()

        self._app = QApplication(sys.argv)
        self._settings = QSettings("GSECARS", "TomoXRD")
        self._model = MainModel(settings=self._settings)
        self._widget = MainWidget(settings=self._settings, paths=self._model.paths)

        self._filename_controller = FilenameController(widget=self._widget)
        self._scanning_controller = ScanningController(
            self._model, widget=self._widget, controller=self._filename_controller
        )
        self._collection_status_controller = CollectionStatusController(
            model=self._model, widget=self._widget, controller=self._scanning_controller
        )

        # Application worker thread
        self._main_worker = QtWorkerModel(self._worker_methods, ())
        self._main_worker.start()

    @staticmethod
    def _window_enumeration_handler(handle: int, windows: list) -> None:
        """Populates the list of open windows."""
        windows.append((handle, win32gui.GetWindowText(handle)))

    def _check_for_existing_application(self, version: str) -> None:
        """If an application instance is already open it brings the application to top-most."""
        # Get open windows list for Windows OS
        if sys.platform == "win32":
            windows = []
            win32gui.EnumWindows(self._window_enumeration_handler, windows)

            # Check the list for application instance
            for window in windows:
                if f"TomoXRD {version}" in window[1]:
                    win32gui.ShowWindow(window[0], 5)
                    win32gui.SetForegroundWindow(window[0])
                    sys.exit()

    def _worker_methods(self) -> None:
        """Runs all the worker methods."""
        while not self._widget.terminated:
            self._collection_status_controller.update_collection_status()
            time.sleep(0.05)

        # Clear camonitor instances after exiting the loop
        for pv in self._model.bmd.collection:
            pv.moving = False
            del pv

        # Set as finished so UI can exit
        self._widget.workers_finished = True

    def run(self, version: str) -> None:
        """Starts the application."""
        # Limit the number of application instances to one
        self._check_for_existing_application(version=version)

        self._widget.display(
            version=version,
            window_size=self._settings.value("window_size"),
            window_position=self._settings.value("window_position"),
            window_state=self._settings.value("maximized"),
        )
        sys.exit(self._app.exec())
