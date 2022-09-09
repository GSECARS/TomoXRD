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
from qtpy.QtGui import QWheelEvent
from qtpy.QtWidgets import QAbstractSpinBox, QDoubleSpinBox
from typing import Optional


class NumberSpinBox(QDoubleSpinBox):
    """
    Used to create instances of numeric only spin boxes without arrow buttons.
    """

    def __init__(
        self,
        min_value: float,
        max_value: float,
        default_value: float,
        single_step: float,
        precision: Optional[int] = 0,
        size: Optional[QSize] = None,
        object_name: Optional[str] = "number-spinbox",
    ) -> None:
        super(NumberSpinBox, self).__init__()

        self._min_value = min_value
        self._max_value = max_value
        self._default_value = default_value
        self._single_step = single_step
        self._precision = precision
        self._object_name = object_name

        # Set size
        if size is not None:
            self.setFixedSize(size)

        self._set_min_max_values()
        self._set_single_precision_values()
        self._set_default_value()
        self._config_spinbox()

    def _set_min_max_values(self) -> None:
        """Checks the min and max values and set them as the spinbox range."""
        if self._min_value >= self._max_value:
            raise ValueError("The min value must be lower than the max value.")

        self.setMinimum(self._min_value)
        self.setMaximum(self._max_value)

    def _set_default_value(self) -> None:
        """Checks and set the default value for the spinbox."""
        if (
            self._default_value > self._max_value
            or self._default_value < self._min_value
        ):
            raise ValueError(
                "The default value must be within the range of the acceptable values for the spinbox."
            )
        self.setValue(self._default_value)

    def _set_single_precision_values(self) -> None:
        """Checks the single step and precision."""
        # Check and set the single step
        if self._single_step > abs(self._max_value - self._min_value) / 3:
            raise ValueError(
                "The single step given must be maximum 1/3 of the total range of the spinbox."
            )
        self.setSingleStep(self._single_step)

        # Check and set the precision
        if self._precision < 0:
            raise ValueError("Precision value can't be lesser than 0.")
        self.setDecimals(self._precision)

    def _config_spinbox(self) -> None:
        """Sets the basic configuration values for the spinbox."""
        # Set object name
        if self._object_name is not None:
            self.setObjectName(self._object_name)

        # Align to center
        self.setAlignment(Qt.AlignCenter)

        # Disable buttons
        self.setButtonSymbols(QAbstractSpinBox.NoButtons)

        # Connect lineedit
        self.lineEdit().returnPressed.connect(self._return_pressed_event)

    def _return_pressed_event(self) -> None:
        """Clears the focus"""
        self.clearFocus()


class NoWheelNumberSpinBox(NumberSpinBox):
    """
    Used to create instances of NumberSpinBox that have the wheel events disabled.
    """

    def __init__(
        self,
        min_value: float,
        max_value: float,
        default_value: float,
        single_step: float,
        size: Optional[QSize] = None,
        precision: Optional[int] = 0,
        object_name: Optional[str] = "number-spinbox",
    ) -> None:
        super(NoWheelNumberSpinBox, self).__init__(
            min_value=min_value,
            max_value=max_value,
            default_value=default_value,
            single_step=single_step,
            precision=precision,
            size=size,
            object_name=object_name,
        )

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Sets the behavior for the wheel events."""
        # Ignore wheel events
        event.ignore()
