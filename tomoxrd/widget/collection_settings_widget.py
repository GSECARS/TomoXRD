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
        self._lbl_omega_range_start = AbstractLabel("Ω Range Start")
        self._lbl_omega_range_end = AbstractLabel("Ω Range End")
        self._lbl_step_size = AbstractLabel("Step Size (°)")
        self._lbl_map_options = AbstractLabel(
            "Map Options (under construction)", object_name="lbl-map"
        )

        # Combo box
        self.combo_collection_type = AbstractComboBox(
            size=QSize(95, 22), object_name="combo-collection"
        )

        # Spin boxes
        self.spin_exposure = NoWheelNumberSpinBox(
            min_value=0.05,
            max_value=300,
            default_value=1.0,
            single_step=0.5,
            precision=4,
            size=QSize(95, 22),
            object_name="spinbox-collection",
        )
        self.spin_omega_range_start = NoWheelNumberSpinBox(
            min_value=-360.0,
            max_value=360.0,
            default_value=0.0,
            single_step=1.0,
            precision=4,
            size=QSize(95, 22),
            object_name="spinbox-collection",
        )
        self.spin_omega_range_end = NoWheelNumberSpinBox(
            min_value=-360.0,
            max_value=360.0,
            default_value=80.0,
            single_step=1.0,
            precision=4,
            size=QSize(95, 22),
            object_name="spinbox-collection",
        )
        self.spin_step_size = NoWheelNumberSpinBox(
            min_value=0.001,
            max_value=15,
            default_value=0.5,
            single_step=0.1,
            precision=4,
            size=QSize(95, 22),
            object_name="spinbox-collection",
        )

        self._configure_collection_settings_groupbox()
        self._layout_collection_settings()

    def _configure_collection_settings_groupbox(self) -> None:
        """Base configuration of the collection settings widgets."""
        # Load groupbox qss file
        self.setStyleSheet(
            open(
                os.path.join(self._paths.qss_path, "collection_settings.qss"), "r"
            ).read()
        )

        # Set groupbox title
        self.setTitle(self._title)

        # Add collection types
        self.combo_collection_type.addItems(["Still", "Step", "Wide"])
        self.combo_collection_type.currentIndexChanged.connect(self._toggle_widget_status)
        self.combo_collection_type.setCurrentIndex(1)

    def _toggle_widget_status(self) -> None:
        if self.combo_collection_type.currentText() == "Still":
            self._lbl_step_size.setEnabled(False)
            self._lbl_omega_range_start.setEnabled(False)
            self._lbl_omega_range_end.setEnabled(False)
            self.spin_step_size.setEnabled(False)
            self.spin_omega_range_start.setEnabled(False)
            self.spin_omega_range_end.setEnabled(False)
        elif self.combo_collection_type.currentText() == "Step":
            self._lbl_step_size.setEnabled(True)
            self._lbl_omega_range_start.setEnabled(True)
            self._lbl_omega_range_end.setEnabled(True)
            self.spin_step_size.setEnabled(True)
            self.spin_omega_range_start.setEnabled(True)
            self.spin_omega_range_end.setEnabled(True)
        else:
            self._lbl_step_size.setEnabled(False)
            self._lbl_omega_range_start.setEnabled(True)
            self._lbl_omega_range_end.setEnabled(True)
            self.spin_step_size.setEnabled(False)
            self.spin_omega_range_start.setEnabled(True)
            self.spin_omega_range_end.setEnabled(True)

    def _layout_collection_settings(self) -> None:
        """Layout collection settings widgets."""
        layout_collection = QGridLayout()
        layout_collection.addWidget(
            self._lbl_collection_type, 0, 3, 1, 1, alignment=Qt.AlignmentFlag.AlignRight
        )
        layout_collection.addWidget(self.combo_collection_type, 0, 4, 1, 1)
        layout_collection.addWidget(
            self._lbl_omega_range_start,
            1,
            1,
            1,
            1,
            alignment=Qt.AlignmentFlag.AlignRight,
        )
        layout_collection.addWidget(self.spin_omega_range_start, 1, 2, 1, 1)
        layout_collection.addWidget(
            self._lbl_omega_range_end, 1, 3, 1, 1, alignment=Qt.AlignmentFlag.AlignRight
        )
        layout_collection.addWidget(self.spin_omega_range_end, 1, 4, 1, 1)
        layout_collection.addWidget(
            self._lbl_step_size, 2, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignRight
        )
        layout_collection.addWidget(self.spin_step_size, 2, 2, 1, 1)
        layout_collection.addWidget(
            self._lbl_exposure, 2, 3, 1, 1, alignment=Qt.AlignmentFlag.AlignRight
        )
        layout_collection.addWidget(self.spin_exposure, 2, 4, 1, 1)
        layout_collection.addWidget(
            self._lbl_map_options, 4, 1, 1, 4, alignment=Qt.AlignmentFlag.AlignCenter
        )

        layout_collection.setColumnStretch(0, 1)
        layout_collection.setColumnStretch(5, 1)

        self.setLayout(layout_collection)
