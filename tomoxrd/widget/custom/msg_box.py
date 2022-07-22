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

from qtpy.QtWidgets import QMessageBox


class MsgBox(QMessageBox):
    """Custom popup message box widget to expand to the available space."""

    def __init__(self, msg: str):
        super(MsgBox, self).__init__()

        self.setStyleSheet(
            "QMessageBox, QMessageBox * {"
            "background: #222a35;"
            "color: #afabab;"
            "}"
            "QPushButton {"
            "background: #344152;"
            "color: #e6e6e6;"
            "border: 1px solid #e6e6e6;"
            "font-family: 'Times New Roman';"
            "font-size: 16px;"
            "border-radius: 4px;"
            "padding: 5px 20px;"
            "}"
            "QPushButton:hover, QPushButton:focus {"
            "background: #e6e6e6;"
            "color: #344152;"
            "}"
        )

        self.critical(self, "Error", msg, QMessageBox.Ok)
