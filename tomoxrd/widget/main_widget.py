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

import os
from qtpy.QtCore import QPoint, QSettings, QSize, Qt, QEvent
from qtpy.QtGui import QCloseEvent, QIcon
from qtpy.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QFrame,
    QGridLayout,
)
from typing import Optional

from tomoxrd.model import PathModel
from tomoxrd.widget import (
    FilenameSettingsWidget,
    CollectionSettingsWidget,
    CollectionPointsWidget,
    CollectionStatusWidget,
)


class MainWidget(QMainWindow):
    """
    The main application window.
    """

    def __init__(self, settings: QSettings, paths: PathModel) -> None:
        super(MainWidget, self).__init__()

        self._settings = settings
        self._paths = paths

        self._central_widget = QFrame()
        self.filename_settings = FilenameSettingsWidget(paths=self._paths)
        self.collection_settings = CollectionSettingsWidget(paths=self._paths)
        self.collection_points = CollectionPointsWidget(paths=self._paths)
        self.collection_status = CollectionStatusWidget(paths=self._paths)

        # Event helpers
        self._terminated: bool = False
        self._workers_finished: bool = False

        self._configure_main_frame()
        self._configure_main_widget()

    def _configure_main_frame(self) -> None:
        """Configures the main frame widget (central widget)."""
        layout = QGridLayout()
        layout.addWidget(self.filename_settings, 0, 0, 1, 1)
        layout.addWidget(self.collection_settings, 0, 1, 1, 1)
        layout.addWidget(self.collection_points, 1, 0, 1, 2)
        layout.addWidget(self.collection_status, 2, 0, 1, 2)

        layout.setRowStretch(1, 1)
        layout.setColumnStretch(1, 1)

        self._central_widget.setLayout(layout)

    def _configure_main_widget(self) -> None:
        """Configuration of the main window."""
        # Set the object name
        self.setObjectName("QMainWindow")

        # Enable the status bar
        self.statusBar()

        # Set the icon
        self.setWindowIcon(
            QIcon(os.path.join(self._paths.icon_path, "tomoxrd_icon.png"))
        )

        # Load qss
        self.setStyleSheet(
            open(os.path.join(self._paths.qss_path, "main.qss"), "r").read()
        )

        # Set central widget
        self.setCentralWidget(self._central_widget)

        # Set starting focus
        self.setFocus()

    def display(
        self,
        version: str,
        window_size: Optional[QSize] = None,
        window_position: Optional[QPoint] = None,
        window_state: Optional[int] = None,
    ) -> None:
        """Display, resize, move and set the main application window title."""

        self.setWindowTitle(f"TomoXRD {version}")  # Set the title
        self.showNormal()  # Display

        # Resize
        if window_size is not None:
            self.resize(window_size)

        # Move
        if window_position is not None:
            self.move(window_position)

        # Set window state
        if window_state is not None:
            if window_state == 2:
                self.setWindowState(Qt.WindowMaximized)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Creates a message box for exit confirmation if closeEvent is triggered."""
        _msg_question = QMessageBox.question(
            self,
            "Exit confirmation",
            "Are you sure you want to close the application?",
            defaultButton=QMessageBox.No,
        )

        if _msg_question == QMessageBox.Yes:
            # Save the main application window size, position and state.
            self._settings.setValue("window_size", self.size())
            self._settings.setValue("window_position", self.pos())
            self._settings.setValue("maximized", int(self.windowState()))

            # Make sure that all other threads are aborted before closing.
            self._terminated = True
            while not self._workers_finished:
                continue

            # Close application
            event.accept()
        else:
            event.ignore()

    def changeEvent(self, event: QEvent) -> None:
        """Updates the state of the window on changes"""
        if event.type() == QEvent.WindowStateChange:
            # Center the window to screen after
            if event.oldState() & Qt.WindowMaximized:
                center = self.screen().availableGeometry().center()

                # Position the window in the middle of the active screen
                x = int(center.x() - self.width() / 2)
                y = int(center.y() - self.height() / 2)
                self.setGeometry(x, y, 250, 250)

    @property
    def terminated(self) -> bool:
        return self._terminated

    @property
    def workers_finished(self) -> bool:
        return self._workers_finished

    @workers_finished.setter
    def workers_finished(self, value: bool) -> None:
        self._workers_finished = value
