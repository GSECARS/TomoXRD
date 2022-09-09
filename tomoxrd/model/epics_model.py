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
from enum import Enum
from epics import pv

from tomoxrd.widget.custom import MsgBox


class EpicsConnectionError(Exception):
    """No epics connection exception."""

    def __init__(self, message) -> None:
        super(EpicsConnectionError, self).__init__(message)
        self._message = message

    @property
    def message(self) -> str:
        MsgBox(msg=self._message)
        return f"[Epics-Connection-Error] - {self._message}"


class EpicsConfig(Enum):
    """Empty Enum to be populated with PVs"""
    detector_x = "13BMD:m121"
    detector_z = "13BMD:m70"


@dataclass(frozen=False)
class EpicsModel:
    """Base epics model, used for testing the connection with all PVs given."""

    _connected: bool = field(init=False, compare=False, repr=False, default=False)

    def connect(self) -> None:
        """Check and set the connection status of all PVs included in the EpicsConfig."""
        if not len(EpicsConfig):
            return None

        for name, member in EpicsConfig.__members__.items():

            if not len(member.value) > 2:
                value = member.value[0]
            else:
                value = member.value

            try:
                pv_check = pv.get_pv(value, connect=True)
                if not pv_check.connected:
                    raise EpicsConnectionError(f"Could not connect {name} ({value})")
            except EpicsConnectionError:
                return None

        object.__setattr__(self, "_connected", True)

    @property
    def connected(self) -> bool:
        return self._connected
