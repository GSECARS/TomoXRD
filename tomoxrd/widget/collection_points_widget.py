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
from qtpy.QtCore import QSize, Qt
from qtpy.QtWidgets import QGroupBox, QGridLayout

from tomoxrd.model import PathModel
from tomoxrd.widget.custom import AbstractFlatButton, AbstractTableWidget


class CollectionPointsWidget(QGroupBox):

    _title: str = "Collection Points"

    def __init__(self, paths: PathModel) -> None:
        super(CollectionPointsWidget, self).__init__()

        # The assets path
        self._paths = paths

        # Buttons
        self.btn_add = AbstractFlatButton("Add", size=QSize(85, 22), object_name="btn-points")
        self.btn_delete = AbstractFlatButton("Delete", size=QSize(85, 22), object_name="btn-points")
        self.btn_clear = AbstractFlatButton("Clear", size=QSize(85, 22), object_name="btn-points")
        self.btn_check_all = AbstractFlatButton("Check all", size=QSize(85, 22), object_name="btn-points")

        # Tables
        self.table_points = AbstractTableWidget(
            columns=5,
            horizontal_headers=["Name", "X", "Y", "Z", "Enabled"],
            column_stretch=0,
            object_name="table-points"
        )

        self._configure_collection_points_groupbox()
        self._layout_collection_points()

    def _configure_collection_points_groupbox(self) -> None:
        """Base configuration of the collection points widgets."""
        # Load groupbox qss file
        self.setStyleSheet(
            open(
                os.path.join(self._paths.qss_path, "collection_points.qss"), "r"
            ).read()
        )

        # Set groupbox title
        self.setTitle(self._title)

    def _layout_collection_points(self) -> None:
        layout_points = QGridLayout()
        layout_points.addWidget(self.btn_add, 0, 1, 1, 1)
        layout_points.addWidget(self.btn_delete, 0, 2, 1, 1)
        layout_points.addWidget(self.btn_clear, 0, 3, 1, 1)
        layout_points.addWidget(self.btn_check_all, 0, 4, 1, 1)
        layout_points.addWidget(self.table_points, 1, 0, 1, 5)

        layout_points.setColumnStretch(0, 1)
        layout_points.setRowStretch(1, 1)

        self.setLayout(layout_points)
