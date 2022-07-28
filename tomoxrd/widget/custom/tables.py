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

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QTableWidget, QAbstractItemView, QHeaderView, QTableWidgetItem, QCheckBox, QHBoxLayout
from typing import Optional

from tomoxrd.widget.custom import AbstractLabel, AbstractInputBox


class AbstractTableWidget(QTableWidget):
    """
    Used to create instances of simple table widgets, with a specified number of columns.
    """

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
            if self._column_stretch >= 0 and self._column_stretch <= self._columns - 1:
                self.horizontalHeader().setSectionResizeMode(self._column_stretch, QHeaderView.Stretch)

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

        self.add_point()
        self.add_point()
        self.add_point()

    def add_point(self) -> None:

        row = self.rowCount()
        self.setRowCount(row + 1)

        # Name
        name = AbstractLabel("pos1")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCellWidget(row, 0, name)

        # x value
        x = AbstractInputBox(object_name="table-input")
        x.setText("1.0300")
        self.setCellWidget(row, 1, x)

        # y value
        y = AbstractInputBox(object_name="table-input")
        y.setText("1.0200")
        self.setCellWidget(row, 2, y)

        # z value
        z = AbstractInputBox(object_name="table-input")
        z.setText("1.0100")
        self.setCellWidget(row, 3, z)

        # Enabled
        checkbox = QCheckBox()
        checkbox.setChecked(True)
        checkbox.setObjectName("table-checkbox")
        self.setCellWidget(row, 4, checkbox)

