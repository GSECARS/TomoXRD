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
from qtpy.QtWidgets import QGroupBox, QGridLayout, QCheckBox

from tomoxrd.model import PathModel, EventFilterModel
from tomoxrd.widget.custom import (
    AbstractFlatButton,
    FileBrowserButton,
    AbstractLabel,
    AbstractInputBox,
    NumberSpinBox,
)


class FilenameSettingsWidget(QGroupBox):

    _title: str = "Filename Settings"

    def __init__(self, paths: PathModel) -> None:
        super(FilenameSettingsWidget, self).__init__()

        # The assets paths
        self._paths = paths

        # Labels
        self._lbl_filename = AbstractLabel("Filename")
        self._lbl_path = AbstractLabel("Path")
        self._lbl_frame_number = AbstractLabel("Frame #")
        self.lbl_calibration_path = AbstractLabel()

        # Input boxes
        self.ipt_filename = AbstractInputBox(size=QSize(115, 22))
        self.ipt_path = AbstractInputBox(size=QSize(115, 22))

        # Buttons
        self.btn_reset = AbstractFlatButton(
            "Reset", size=QSize(85, 22), object_name="btn-filename-settings"
        )
        self.flb_path = FileBrowserButton(
            "??????", size=QSize(25, 22), object_name="btn-filename-settings"
        )
        self.flb_calibration = FileBrowserButton(
            "Load Calibration",
            single_file=True,
            size=QSize(200, 22),
            object_name="btn-filename-settings",
        )

        # Spin boxes
        self.spin_frame_number = NumberSpinBox(
            min_value=1,
            max_value=100000,
            default_value=1,
            single_step=1,
            object_name="frame-spinbox",
        )

        # Check boxes
        self.check_chrysalis = QCheckBox("Use CrysAlis")
        self.check_auto_reset_frames = QCheckBox("Auto Reset Frame #")

        # Event filters
        self._filename_filter = EventFilterModel(as_filepath=False)
        self._filepath_filter = EventFilterModel(as_filepath=True)

        self._configure_filename_settings_groupbox()
        self._layout_filename_settings()

    def _configure_filename_settings_groupbox(self) -> None:
        """Base configuration of the filename settings widgets."""
        # Load groupbox qss file
        self.setStyleSheet(
            open(
                os.path.join(self._paths.qss_path, "filename_settings.qss"), "r"
            ).read()
        )

        # Set groupbox title
        self.setTitle(self._title)

        # Checkbox object name
        self.check_auto_reset_frames.setObjectName("check-filename-settings")

        # Set checkboxes check status
        self.check_auto_reset_frames.setChecked(True)
        self.check_chrysalis.setChecked(True)

        # Add event filters
        self.ipt_filename.installEventFilter(self._filename_filter)
        self.ipt_path.installEventFilter(self._filepath_filter)

        # Connect reset button
        self.btn_reset.clicked.connect(self._reset_frame_number)

    def update_frame_number(self, frame: int) -> None:
        if frame >= 1:
            self.spin_frame_number.setValue(frame)

    def _reset_frame_number(self) -> None:
        self.spin_frame_number.setValue(1)

    def _layout_filename_settings(self) -> None:
        layout = QGridLayout()
        layout.addWidget(self._lbl_filename, 0, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.ipt_filename, 0, 1, 1, 2)
        layout.addWidget(self._lbl_path, 1, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.ipt_path, 1, 1, 1, 2)
        layout.addWidget(self.flb_path, 1, 3, 1, 1)
        layout.addWidget(self._lbl_frame_number, 2, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.spin_frame_number, 2, 1, 1, 1)
        layout.addWidget(self.btn_reset, 2, 2, 1, 2)
        layout.addWidget(self.check_auto_reset_frames, 3, 0, 1, 3)
        layout.addWidget(self.check_chrysalis, 4, 0, 1, 3)
        layout.addWidget(self.flb_calibration, 5, 0, 1, 4)
        layout.addWidget(self.lbl_calibration_path, 6, 0, 1, 4)

        self.setLayout(layout)
