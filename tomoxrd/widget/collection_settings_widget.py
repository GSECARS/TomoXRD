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
from tomoxrd.widget.custom import AbstractComboBox, AbstractLabel, NoWheelNumberSpinBox


class CollectionSettingsWidget(QGroupBox):

    _title: str = "Collection Settings"

    def __init__(self, paths: PathModel) -> None:
        super(CollectionSettingsWidget, self).__init__()

        # The assets path
        self._paths = paths

        # Labels
        self._lbl_collection_type = AbstractLabel("Collection Type")
        self._lbl_exposure = AbstractLabel("Exposure (s)")
        self._lbl_omega_range = AbstractLabel("Ω Range (±)")
        self._lbl_step_size = AbstractLabel("Step Size (°)")
        self._lbl_map_options = AbstractLabel(
            "Map Options (under construnction)", object_name="lbl-map"
        )

        # Combo box
        self.combo_collection_type = AbstractComboBox(
            size=QSize(95, 22), object_name="combo-collection"
        )

        # Spin boxes
        self.spin_exposure = NoWheelNumberSpinBox(
            min_value=0.001,
            max_value=15,
            default_value=0.1,
            single_step=0.1,
            precision=4,
            size=QSize(95, 22),
            object_name="spinbox-collection",
        )
        self.spin_omega_range = NoWheelNumberSpinBox(
            min_value=0.001,
            max_value=15,
            default_value=0.1,
            single_step=0.1,
            precision=4,
            size=QSize(95, 22),
            object_name="spinbox-collection",
        )
        self.spin_step_size = NoWheelNumberSpinBox(
            min_value=0.001,
            max_value=15,
            default_value=0.1,
            single_step=0.1,
            precision=4,
            size=QSize(95, 22),
            object_name="spinbox-collection",
        )

        self._configure_collection_settings_groupbox()
        self._layout_collection_settings()

    def _configure_collection_settings_groupbox(self) -> None:
        """Base configuration of the collection settinghs widgets."""
        # Load groupbox qss file
        self.setStyleSheet(
            open(
                os.path.join(self._paths.qss_path, "collection_settings.qss"), "r"
            ).read()
        )

        # Set groupbox title
        self.setTitle(self._title)

    def _layout_collection_settings(self) -> None:
        """Layou collection settings widgets."""
        layout_collection = QGridLayout()
        layout_collection.addWidget(
            self._lbl_collection_type, 0, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignRight
        )
        layout_collection.addWidget(self.combo_collection_type, 0, 2, 1, 1)
        layout_collection.addWidget(
            self._lbl_exposure, 1, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignRight
        )
        layout_collection.addWidget(self.spin_exposure, 1, 2, 1, 1)
        layout_collection.addWidget(
            self._lbl_omega_range, 2, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignRight
        )
        layout_collection.addWidget(self.spin_omega_range, 2, 2, 1, 1)
        layout_collection.addWidget(
            self._lbl_step_size, 3, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignRight
        )
        layout_collection.addWidget(self.spin_step_size, 3, 2, 1, 1)

        layout_collection.addWidget(
            self._lbl_map_options, 4, 1, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter
        )

        layout_collection.setColumnStretch(0, 1)
        layout_collection.setColumnStretch(3, 1)

        self.setLayout(layout_collection)
