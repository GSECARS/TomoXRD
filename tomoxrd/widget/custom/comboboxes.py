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

from qtpy.QtCore import QSize
from qtpy.QtGui import QMouseEvent
from qtpy.QtWidgets import QComboBox
from typing import Optional


class AbstractComboBox(QComboBox):
    """
    Used to create instances of numeric only spin boxes without arrow buttons.
    """

    def __init__(
        self,
        size: Optional[QSize] = None,
        object_name: Optional[str] = "abstract-combobox",
    ) -> None:
        super(AbstractComboBox, self).__init__()

        self._size = size
        self._object_name = object_name

        self._config_combobox()

    def _config_combobox(self) -> None:
        """Sets the basic configuration values for the spinbox."""
        # Set object name
        if self._object_name is not None:
            self.setObjectName(self._object_name)

        # Set size
        if self._size is not None:
            self.setFixedSize(self._size)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.showPopup()
