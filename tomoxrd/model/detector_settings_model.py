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

from dataclasses import dataclass, field
from qtpy.QtCore import QSettings


@dataclass
class DetectorSettingsModel:

    settings: QSettings = field(init=True, compare=False)

    _tomo_x: float = field(init=False, compare=False, default=-127.00)
    _tomo_z: float = field(init=False, compare=False, default=50.00)
    _xrd_x: float = field(init=False, compare=False, default=95.00)
    _xrd_z: float = field(init=False, compare=False, default=0.00)
    _detector_out: float = field(init=False, compare=False, default=100.00)

    def __post_init__(self) -> None:

        # Set tomo x value
        tomo_x_value = self.settings.value("tomo_x", type=float)
        if tomo_x_value is None:
            tomo_x_value = -127.00
        object.__setattr__(self, "_tomo_x", tomo_x_value)

        # Set tomo z value
        tomo_z_value = self.settings.value("tomo_z", type=float)
        if tomo_z_value is None:
            tomo_z_value = 50.00
        object.__setattr__(self, "_tomo_z", tomo_z_value)

        # Set xrd x value
        xrd_x_value = self.settings.value("xrd_x", type=float)
        if xrd_x_value is None:
            xrd_x_value = 95.00
        object.__setattr__(self, "_xrd_x", xrd_x_value)

        # Set xrd z value
        xrd_z_value = self.settings.value("xrd_z", type=float)
        if xrd_z_value is None:
            xrd_z_value = 0.00
        object.__setattr__(self, "_xrd_z", xrd_z_value)

        # Set detector out value
        detector_out_value = self.settings.value("detector_out", type=float)
        if detector_out_value is None:
            detector_out_value = 100.00
        object.__setattr__(self, "_detector_out", detector_out_value)

    @property
    def tomo_x(self) -> float:
        return self._tomo_x

    @property
    def tomo_z(self) -> float:
        return self._tomo_z

    @property
    def xrd_x(self) -> float:
        return self._xrd_x

    @property
    def xrd_z(self) -> float:
        return self._xrd_z

    @property
    def detector_out(self) -> float:
        return self._detector_out

    @tomo_x.setter
    def tomo_x(self, value: float) -> None:
        object.__setattr__(self, "_tomo_x", value)
        self.settings.setValue("tomo_x", self._tomo_x)

    @tomo_z.setter
    def tomo_z(self, value: float) -> None:
        object.__setattr__(self, "_tomo_z", value)
        self.settings.setValue("tomo_z", self._tomo_z)

    @xrd_x.setter
    def xrd_x(self, value: float) -> None:
        object.__setattr__(self, "_xrd_x", value)
        self.settings.setValue("xrd_x", self._xrd_x)

    @xrd_z.setter
    def xrd_z(self, value: float) -> None:
        object.__setattr__(self, "_xrd_z", value)
        self.settings.setValue("xrd_z", self._xrd_z)

    @detector_out.setter
    def detector_out(self, value: float) -> None:
        object.__setattr__(self, "_detector_out", value)
        self.settings.setValue("detector_out", self._detector_out)
