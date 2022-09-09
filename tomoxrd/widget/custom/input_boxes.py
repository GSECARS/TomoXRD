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

from qtpy.QtCore import QSize, Qt
from qtpy.QtWidgets import QLineEdit
from typing import Optional


class AbstractInputBox(QLineEdit):
    """
    Used to create instances of simple LineEdit widgets.
    """

    def __init__(
        self,
        placeholder: Optional[str] = None,
        size: Optional[QSize] = None,
        object_name: Optional[str] = "abstract-input",
        as_filepath: Optional[bool] = False,
    ) -> None:
        super(AbstractInputBox, self).__init__()

        self._placeholder = placeholder
        self._size = size
        self._object_name = object_name

        self._config_abstract_input_box()

    def _config_abstract_input_box(self) -> None:
        """Sets the basic configuration values for the abstract input boxes."""
        # Set center alignment
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Set placeholder text
        if self._placeholder is not None:
            self.setPlaceholderText(self._placeholder)

        # Set object name
        if self._object_name is not None:
            self.setObjectName(self._object_name)

        # Set size
        if self._size is not None:
            self.setFixedSize(self._size)

        # Connect return pressed event.
        self.returnPressed.connect(self._return_pressed_event)

    def _return_pressed_event(self) -> None:
        """Clears the focus"""
        self.clearFocus()

