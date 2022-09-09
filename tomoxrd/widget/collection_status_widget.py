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
import datetime
from qtpy.QtCore import QSize, Qt
from qtpy.QtWidgets import QWidget, QGridLayout
from typing import Optional

from tomoxrd.model import PathModel
from tomoxrd.widget.custom import AbstractLabel, AbstractFlatButton


class CollectionStatusWidget(QWidget):
    def __init__(self, paths: PathModel) -> None:
        super(CollectionStatusWidget, self).__init__()

        # The assets path
        self._paths = paths

        # Labels
        self._lbl_est_time = AbstractLabel("Estimated Time")
        self._lbl_elp_time = AbstractLabel("Elapsed Time")
        self.lbl_status = AbstractLabel("Idle", object_name="lbl-status")
        self.lbl_estimated_time = AbstractLabel("00:00:00")
        self.lbl_elapsed_time = AbstractLabel("00:00:00")
        self.lbl_frames = AbstractLabel("0/0 Frames")
        self.lbl_collections = AbstractLabel("0/1 Collections")

        # Buttons
        self.btn_collect_abort = AbstractFlatButton(
            "Collect", size=QSize(135, 68), object_name="btn-status"
        )
        self.btn_prepare_for_tomo = AbstractFlatButton(
            "Prepare for Tomo", size=QSize(135, 30), object_name="btn-status"
        )
        self.btn_prepare_for_xrd = AbstractFlatButton(
            "Prepare for XRD", size=QSize(135, 30), object_name="btn-status"
        )

        self._configure_collection_status_widgets()
        self._layout_collection_status()

    def update_estimated_time_widget(self, seconds: float) -> None:
        time_delta = datetime.timedelta(seconds=seconds)
        time_delta = time_delta - datetime.timedelta(microseconds=time_delta.microseconds)
        self.lbl_estimated_time.setText(str(time_delta))

    def update_elapsed_time_widget(self, seconds: float) -> None:
        time_delta = datetime.timedelta(seconds=seconds)
        time_delta = time_delta - datetime.timedelta(microseconds=time_delta.microseconds)
        self.lbl_elapsed_time.setText(str(time_delta))

    def toggle_tomo_abort_button(self, state: bool) -> None:
        """Toggles the style to account for prepare for tomo and abort."""
        if not state:
            self.btn_prepare_for_tomo.setText("Prepare for Tomo")
            self.btn_prepare_for_tomo.setStyleSheet(
                """
                QPushButton {
                    background: #9dedca;
                    border: 2px solid #9dedca;
                    color: #323336;
                    font-size: 16px;
                    padding: 1px 5px;
                }
                QPushButton:hover, QPushButton:focus, QPushButton:pressed {
                    background-color: #71ab91;
                    border-color: #71ab91;
                }
                """
            )
        else:
            self.btn_prepare_for_tomo.setText("Abort")
            self.btn_prepare_for_tomo.setStyleSheet(
                """
                QPushButton {
                    background: #99232f;
                    border: 2px solid #99232f;
                    color: #d5dde3;
                    font-size: 16px;
                    padding: 1px 5px;
                }
                QPushButton:hover, QPushButton:focus, QPushButton:pressed {
                    background-color: #731e26;
                    border-color: #731e26;
                }
                """
            )

    def toggle_xrd_abort_button(self, state: bool) -> None:
        """Toggles the style to account for prepare for tomo and abort."""
        if not state:
            self.btn_prepare_for_xrd.setText("Prepare for XRD")
            self.btn_prepare_for_xrd.setStyleSheet(
                """
                QPushButton {
                    background: #9dedca;
                    border: 2px solid #9dedca;
                    color: #323336;
                    font-size: 16px;
                    padding: 1px 5px;
                }
                QPushButton:hover, QPushButton:focus, QPushButton:pressed {
                    background-color: #71ab91;
                    border-color: #71ab91;
                }
                """
            )
        else:
            self.btn_prepare_for_xrd.setText("Abort")
            self.btn_prepare_for_xrd.setStyleSheet(
                """
                QPushButton {
                    background: #99232f;
                    border: 2px solid #99232f;
                    color: #d5dde3;
                    font-size: 16px;
                    padding: 1px 5px;
                }
                QPushButton:hover, QPushButton:focus, QPushButton:pressed {
                    background-color: #731e26;
                    border-color: #731e26;
                }
                """
            )

    def toggle_collect_abort_button(self, state: bool) -> None:
        """Toggles the style to account for collect and abort."""
        if not state:
            self.btn_collect_abort.setText("Collect")
            self.btn_collect_abort.setStyleSheet(
                """
                QPushButton {
                    background: #9dedca;
                    border: 2px solid #9dedca;
                    color: #323336;
                    font-size: 16px;
                    padding: 1px 5px;
                }
                QPushButton:hover, QPushButton:focus, QPushButton:pressed {
                    background-color: #71ab91;
                    border-color: #71ab91;
                }
                """
            )
        else:
            self.btn_collect_abort.setText("Abort")
            self.btn_collect_abort.setStyleSheet(
                """
                QPushButton {
                    background: #99232f;
                    border: 2px solid #99232f;
                    color: #d5dde3;
                    font-size: 16px;
                    padding: 1px 5px;
                }
                QPushButton:hover, QPushButton:focus, QPushButton:pressed {
                    background-color: #731e26;
                    border-color: #731e26;
                }
                """
            )

    def _configure_collection_status_widgets(self) -> None:
        # Load the qss file
        self.setStyleSheet(
            open(
                os.path.join(self._paths.qss_path, "collection_status.qss"), "r"
            ).read()
        )

    def update_status_message(self, message: str) -> None:
        self.lbl_status.setText(message)

    def _layout_collection_status(self) -> None:
        """Layout collection status widgets."""
        layout_status = QGridLayout()
        layout_status.setContentsMargins(0, 0, 0, 0)
        layout_status.addWidget(self.lbl_status, 0, 0, 2, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        layout_status.addWidget(self._lbl_est_time, 0, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignRight)
        layout_status.addWidget(self._lbl_elp_time, 1, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignRight)
        layout_status.addWidget(self.lbl_estimated_time, 0, 2, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        layout_status.addWidget(self.lbl_elapsed_time, 1, 2, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        layout_status.addWidget(self.lbl_frames, 0, 3, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        layout_status.addWidget(self.lbl_collections, 1, 3, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        layout_status.addWidget(self.btn_collect_abort, 0, 4, 2, 1)
        layout_status.addWidget(self.btn_prepare_for_tomo, 0, 5, 1, 1)
        layout_status.addWidget(self.btn_prepare_for_xrd, 1, 5, 1, 1)

        layout_status.setColumnStretch(1, 1)
        layout_status.setColumnStretch(2, 1)
        layout_status.setColumnStretch(3, 1)

        self.setLayout(layout_status)
