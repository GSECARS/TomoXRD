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

from qtpy.QtCore import QSettings


def check_float_setting(settings: QSettings, name: str, default: float) -> float:
    """Checks if there is a valid qsetting float value."""
    float_value = float(settings.value(name, type=float))
    if float_value is None:
        float_value = default
    return float_value


def check_str_setting(settings: QSettings, name: str, default: str) -> str:
    """Checks if there is a valid qsetting string value."""
    str_value = str(settings.value(name, type=str))
    if str_value is None:
        str_value = default
    return str_value
