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

from qtpy.QtCore import Qt, QObject, Signal
from qtpy.QtWidgets import (
    QWidget,
    QTableWidget,
    QAbstractItemView,
    QHeaderView,
    QTableWidgetItem,
    QCheckBox,
    QHBoxLayout,
)
from typing import Optional, List

from tomoxrd.widget.custom import AbstractLabel, AbstractInputBox


class AbstractTableWidget(QTableWidget, QObject):
    """
    Used to create instances of simple table widgets, with a specified number of columns.
    """
    enabled_checkboxes_changed: Signal = Signal()

    enabled_checkboxes: List[QCheckBox] = []
    _row_counter: int = 0

    def __init__(
        self,
        columns: Optional[int] = None,
        rows: Optional[int] = None,
        horizontal_headers: Optional[list] = None,
        column_stretch: Optional[int] = None,
        object_name: Optional[str] = "abstract-table",
    ) -> None:
        super(AbstractTableWidget, self).__init__()

        self._columns = columns
        self._rows = rows
        self._horizontal_headers = horizontal_headers
        self._column_stretch = column_stretch
        self._object_name = object_name

        self._configure_abstract_table()

    def _configure_abstract_table(self) -> None:
        """Sets the basic configuration values for the abstract table widget."""
        # Set columns
        if self._columns is not None:
            if self._columns >= 1:
                self.setColumnCount(self._columns)

        # Set rows
        if self._rows is not None:
            if self._rows >= 1:
                self.setRowCount(self._rows)

        # Set horizontal headers
        if self._horizontal_headers is None:
            self.horizontalHeader().setVisible(False)
        else:
            self.horizontalHeader().setVisible(True)
            self.setHorizontalHeaderLabels(self._horizontal_headers)

        # Set object name
        if self._object_name is not None:
            self.setObjectName(self._object_name)

        # Set column stretch
        if self._column_stretch is not None:
            if 0 <= self._column_stretch <= self._columns - 1:
                self.horizontalHeader().setSectionResizeMode(
                    self._column_stretch, QHeaderView.Stretch
                )

        # Hide vertical header
        self.verticalHeader().setVisible(False)

        # Disable grid
        self.setShowGrid(False)

        # Disable header buttons
        self.horizontalHeader().setDisabled(True)

        # Set alternating row colors
        self.setAlternatingRowColors(True)

        # Set selection behavior and mode
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

    def _check_for_available_name(self) -> None:
        self._row_counter = 0
        for row in range(self.rowCount() - 1):

            self._row_counter += 1

            if not f"pos{self._row_counter}" == self.item(row, 0).text():
                return None

    def _checkbox_state_changed(self, state: bool) -> None:
        self.enabled_checkboxes_changed.emit()

    def add_point(
        self,
        x_value: Optional[float] = None,
        y_value: Optional[float] = None,
        z_value: Optional[float] = None,
    ) -> None:

        row = self.rowCount()
        self.setRowCount(row + 1)

        # Name
        self._row_counter = row + 1
        dynamic_created_name = f"pos{self._row_counter}"

        if row > 0:
            # Check if name exists
            for existing_row in range(row):
                if dynamic_created_name == self.item(existing_row, 0).text():
                    temp_counter = self._row_counter
                    self._check_for_available_name()
                    dynamic_created_name = f"pos{self._row_counter}"
                    self._row_counter = temp_counter

        name = QTableWidgetItem(dynamic_created_name)
        name.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, 0, name)

        # x value
        if x_value is not None:
            x = AbstractInputBox(object_name="table-input")
            x.setText(str(x_value))
            self.setCellWidget(row, 1, x)

        # y value
        if y_value is not None:
            y = AbstractInputBox(object_name="table-input")
            y.setText(str(y_value))
            self.setCellWidget(row, 2, y)

        # z value
        if z_value is not None:
            z = AbstractInputBox(object_name="table-input")
            z.setText(str(z_value))
            self.setCellWidget(row, 3, z)

        # Enabled
        checkbox = QCheckBox()
        checkbox.setChecked(True)
        checkbox.setObjectName("table-checkbox")
        self.setCellWidget(row, 4, checkbox)
        self.enabled_checkboxes.append(checkbox)
        checkbox.stateChanged.connect(self._checkbox_state_changed)

    def delete_point(self) -> None:
        index = self.currentRow()
        if index >= 0:
            self.removeRow(index)
            del self.enabled_checkboxes[index]

    def clear_points(self) -> None:
        for row in range(self.rowCount()):
            self.removeRow(row)

        self.setRowCount(0)
        self.enabled_checkboxes.clear()

    def check_all_points(self) -> None:
        for checkbox in self.enabled_checkboxes:
            checkbox.setChecked(True)
