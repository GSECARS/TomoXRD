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

from qtpy.QtCore import QSize, QObject, Signal
from qtpy.QtWidgets import QPushButton, QFileDialog
from typing import Optional


class AbstractFlatButton(QPushButton):
    """
    Used to create instances of simple flat buttons, with or without an icon.
    """

    def __init__(
        self,
        text: Optional[str] = None,
        size: Optional[QSize] = None,
        object_name: Optional[str] = "abstract-button",
    ) -> None:
        super(AbstractFlatButton, self).__init__()

        self._text = text
        self._size = size
        self._object_name = object_name

        self._config_abstract_button()

    def _config_abstract_button(self) -> None:
        """Sets the basic configuration values for the abstract flat button."""
        # Set flat button
        self.setFlat(True)

        # Set text
        if self._text is not None:
            self.setText(self._text)

        # Set object name
        if self._object_name is not None:
            self.setObjectName(self._object_name)

        # Set size
        if self._size is not None:
            self.setFixedSize(self._size)

        # Connect click event
        self.clicked.connect(self._button_click_event)

    def _button_click_event(self) -> None:
        """Clears the focus state of the button."""
        self.clearFocus()


class FileBrowserButton(AbstractFlatButton, QObject):
    """
    Used to create instances of flat buttons that open a QFileDialog to select directory.
    """
    file_path_changed: Signal = Signal(bool)
    folder_path_changed: Signal = Signal(bool)

    def __init__(
        self,
        text: Optional[str] = None,
        single_file: Optional[bool] = False,
        size: Optional[QSize] = None,
        object_name: Optional[str] = "abstract-button"
    ) -> None:
        super(FileBrowserButton, self).__init__(
            text=text,
            size=size,
            object_name=object_name,
        )

        self._single_file = single_file

        self._target_directory = "C:/"
        self._file_path = None
        self._folder_path = None

    def _button_click_event(self) -> None:
        """
        Uses QFileDialog to get the selected path and clears the focus state of the button.
        """
        # Clear the focus state
        self.clearFocus()

        # Open file dialog
        if not self._single_file:
            new_folder_path = QFileDialog.getExistingDirectory(
                parent=self,
                caption="Select Folder",
                directory=self._target_directory
            )
            if new_folder_path != "":
                self._folder_path = new_folder_path
                self.folder_path_changed.emit(True)
        else:
            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.ExistingFile)
            options = QFileDialog.Options()
            new_file_path, _ = QFileDialog.getOpenFileName(
                parent=self,
                caption="Select Calibration File",
                directory=self._target_directory,
                filter="Par File (*.par)",
                options=options,
            )
            if new_file_path != "":
                self._file_path = new_file_path
                self.file_path_changed.emit(True)

    @property
    def target_directory(self) -> str:
        return self._target_directory

    @target_directory.setter
    def target_directory(self, value: str) -> None:
        invalid = '<>"\\|?*#& '
        for char in invalid:
            value = value.replace(char, "_")
        self._target_directory = value

    @property
    def file_path(self) -> str:
        return self._file_path

    @property
    def folder_path(self) -> str:
        return self._folder_path
