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
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGroupBox, QGridLayout

from tomoxrd.model import PathModel
from tomoxrd.widget.custom import AbstractLabel, NumberSpinBox


class DetectorSettingsWidget(QGroupBox):

    _title: str = "Detector Settings"

    def __init__(self, paths: PathModel) -> None:
        super(DetectorSettingsWidget, self).__init__()

        # The assets paths
        self._paths = paths

        # Labels
        self._lbl_warning = AbstractLabel("WARNING!!", object_name="lbl-warning")
        self._lbl_small_description_line_one = AbstractLabel("Used to set detector safe positions")
        self._lbl_small_description_line_two = AbstractLabel("for XRD and TOMO!")
        self._lbl_tomo_x = AbstractLabel("Tomo X")
        self._lbl_tomo_z = AbstractLabel("Tomo Z")
        self._lbl_xrd_x = AbstractLabel("XRD X")
        self._lbl_xrd_z = AbstractLabel("XRD Z")
        self._lbl_detector_out = AbstractLabel("Detector Out")

        # Spin boxes
        self.spin_tomo_x = NumberSpinBox(
            min_value=-100000.00,
            max_value=100000.00,
            default_value=-127.00,
            single_step=1.00,
            precision=2,
            object_name="detector-spinbox",
        )
        self.spin_tomo_z = NumberSpinBox(
            min_value=-100000.00,
            max_value=100000.00,
            default_value=50.00,
            single_step=1.00,
            precision=2,
            object_name="detector-spinbox",
        )
        self.spin_xrd_x = NumberSpinBox(
            min_value=-100000.00,
            max_value=100000.00,
            default_value=95.00,
            single_step=1.00,
            precision=2,
            object_name="detector-spinbox",
        )
        self.spin_xrd_z = NumberSpinBox(
            min_value=-100000.00,
            max_value=100000.00,
            default_value=0.00,
            single_step=1.00,
            precision=2,
            object_name="detector-spinbox",
        )
        self.spin_detector_out = NumberSpinBox(
            min_value=-100000.00,
            max_value=100000.00,
            default_value=100.00,
            single_step=1.00,
            precision=2,
            object_name="detector-spinbox",
        )

        self._configure_detector_settings_groupbox()
        self._layout_detector_settings()

    def _configure_detector_settings_groupbox(self) -> None:
        """Base configuration of the detector settings widgets."""
        # Load groupbox qss file
        self.setStyleSheet(
            open(
                os.path.join(self._paths.qss_path, "detector_settings.qss"), "r"
            ).read()
        )

        # Set groupbox title
        self.setTitle(self._title)

    def _layout_detector_settings(self) -> None:
        layout = QGridLayout()
        layout.addWidget(self._lbl_tomo_x, 0, 0, 1, 1)
        layout.addWidget(self.spin_tomo_x, 0, 1, 1, 1)
        layout.addWidget(self._lbl_xrd_x, 0, 2, 1, 1)
        layout.addWidget(self.spin_xrd_x, 0, 3, 1, 1)
        layout.addWidget(self._lbl_tomo_z, 1, 0, 1, 1)
        layout.addWidget(self.spin_tomo_z, 1, 1, 1, 1)
        layout.addWidget(self._lbl_xrd_z, 1, 2, 1, 1)
        layout.addWidget(self.spin_xrd_z, 1, 3, 1, 1)
        layout.addWidget(self._lbl_detector_out, 2, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.spin_detector_out, 2, 3, 1, 1)
        layout.addWidget(self._lbl_warning, 3, 0, 1, 4, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self._lbl_small_description_line_one, 4, 0, 1, 4, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self._lbl_small_description_line_two, 5, 0, 1, 4, alignment=Qt.AlignmentFlag.AlignLeft)

        layout.setRowStretch(3, 1)

        self.setLayout(layout)
