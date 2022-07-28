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

from qtpy.QtWidgets import QLabel
from typing import Optional


class AbstractLabel(QLabel):
    """
    Used to create instances of simple labels.
    """

    def __init__(
        self,
        text: Optional[str] = None,
        object_name: Optional[str] = "abstract-label",
    ) -> None:
        super(AbstractLabel, self).__init__()

        self._text = text
        self._object_name = object_name

        self._config_abstract_label()

    def _config_abstract_label(self) -> None:
        """Sets the basic configuration values for the abstract labels."""
        # Set text
        if self._text is not None:
            self.setText(self._text)

        # Set object name
        if self._object_name is not None:
            self.setObjectName(self._object_name)
