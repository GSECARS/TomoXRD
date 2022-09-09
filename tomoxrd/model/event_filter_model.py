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
from qtpy.QtCore import QObject, QEvent
from qtpy.QtWidgets import QLineEdit


class EventFilterModel(QObject):
    """Custom event filter model to be used for focus out events."""

    def __init__(self, as_filepath: bool) -> None:
        super(EventFilterModel, self).__init__()
        self._as_filepath = as_filepath

    def eventFilter(self, widget: QLineEdit, event: QEvent) -> bool:
        """ Make available only for FocusOut events. """
        # This will validate the user input of focus out events.
        if event.type() == QEvent.FocusOut:
            # The invalid character values
            if not self._as_filepath:
                invalid = '<>"/\\|?*#& '
            else:
                invalid = '<>"\\|?*#& '

            text = widget.text()
            for char in invalid:
                text = text.replace(char, "_")

            if self._as_filepath:

                if text[-1] != "/":
                    text += "/"

                if not os.path.exists(text):
                    os.makedirs(text)

            widget.setText(text)

        return False
