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
from qtpy.QtWidgets import QWidget, QGridLayout

from tomoxrd.model import PathModel
from tomoxrd.widget.custom import AbstractLabel, AbstractFlatButton


class CollectionStatusWidget(QWidget):
    def __init__(self, paths: PathModel) -> None:
        super(CollectionStatusWidget, self).__init__()

        # The assets path
        self._paths = paths

        # Labels
        self._lbl_time = AbstractLabel("Estimated Time")
        self.lbl_status = AbstractLabel("Idle", object_name="lbl-status")
        self.lbl_estimated_time = AbstractLabel("00:00:00")
        self.lbl_frames = AbstractLabel("0/0 Frames")

        # Buttons
        self.btn_collect_abort = AbstractFlatButton(
            "Collect", size=QSize(135, 60), object_name="btn-status"
        )
        self.btn_prepare_for_method = AbstractFlatButton(
            "Prepare for Tomo", size=QSize(135, 60), object_name="btn-status"
        )

        self._configure_collection_status_widgets()
        self._layout_collection_status()

    def _configure_collection_status_widgets(self) -> None:
        # Load the qss file
        self.setStyleSheet(
            open(
                os.path.join(self._paths.qss_path, "collection_status.qss"), "r"
            ).read()
        )

    def _layout_collection_status(self) -> None:
        """Layout collection status widgets."""
        layout_status = QGridLayout()
        layout_status.setContentsMargins(0, 0, 0, 0)
        layout_status.addWidget(
            self.lbl_status, 0, 0, 2, 1, alignment=Qt.AlignmentFlag.AlignCenter
        )
        layout_status.addWidget(
            self._lbl_time, 0, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignRight
        )
        layout_status.addWidget(
            self.lbl_estimated_time, 0, 2, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft
        )
        layout_status.addWidget(
            self.lbl_frames, 1, 1, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter
        )
        layout_status.addWidget(self.btn_collect_abort, 0, 3, 2, 1)
        layout_status.addWidget(self.btn_prepare_for_method, 0, 4, 2, 1)

        layout_status.setColumnStretch(1, 1)
        layout_status.setColumnStretch(2, 1)

        self.setLayout(layout_status)
