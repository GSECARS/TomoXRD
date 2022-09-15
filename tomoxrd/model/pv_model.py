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

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from epics import caget, caput, camonitor, camonitor_clear
from typing import Optional

from tomoxrd.widget.custom import MsgBox


@dataclass(frozen=False)
class PVModel(ABC):
    """Abstract class used to define a PV."""

    pv: str = field(init=True, repr=True, compare=False)
    movable: bool = field(init=True, repr=True, compare=False)
    limited: bool = field(init=True, repr=True, compare=False)
    name: Optional[str] = field(init=True, repr=True, compare=False, default="")
    rbv_extension: Optional[bool] = field(
        init=True, default=False, repr=True, compare=False
    )
    monitor: Optional[bool] = field(init=True, default=False, repr=True, compare=False)

    _rbv_string: str = field(init=False, repr=True, compare=False)
    _moving: bool = field(init=False, repr=False, compare=False, default=True)

    @abstractmethod
    def __post_init__(self) -> None:
        """Runs after the init method."""

    @abstractmethod
    def _monitor_pv(self, **kwargs) -> None:
        """Monitors the PV and changes the readback accordingly."""

    def _create_rbv_string(self) -> None:
        if self.rbv_extension:
            value_string = self.pv + ".RBV"
        else:
            value_string = self.pv
        object.__setattr__(self, "_rbv_string", value_string)

    @property
    def moving(self):
        return self._moving

    @moving.setter
    def moving(self, value):
        if isinstance(value, bool):
            object.__setattr__(self, "_moving", value)

    def __del__(self) -> None:
        camonitor_clear(self._rbv_string)


@dataclass(slots=True)
class DoubleValuePV(PVModel):
    """Used to interact with PVs that work with floats."""

    readback: float = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        self._create_rbv_string()

        if self.monitor:
            object.__setattr__(self, "readback", round(caget(self._rbv_string), 4))
            camonitor(self._rbv_string, callback=self._monitor_pv)

    def _monitor_pv(self, **kwargs) -> None:
        object.__setattr__(self, "readback", round(kwargs["value"], 4))
        object.__setattr__(self, "_moving", True)

    def move(self, value: float, with_limits: Optional[bool] = True, wait: Optional[bool] = False, timeout: Optional[float] = None) -> None:
        """Moves the motor."""

        if not self.movable:
            return None

        if self.moving:
            return None

        if self.limited:
            if with_limits:
                if value < caget(self.pv + ".LLM"):
                    # MsgBox(msg=f"You reach the high limit of the {self.name}.")
                    print(f"You reach the high limit of the {self.name}.")
                    return None
                elif value > caget(self.pv + ".HLM"):
                    # MsgBox(msg=f"You reach the low limit of the {self.name}.")
                    print(f"You reach the low limit of the {self.name}.")
                    return None

        if timeout is not None:
            # Check if moving
            caput(self.pv, value, wait=wait, timeout=timeout)
        else:
            # Check if moving
            caput(self.pv, value, wait=wait)

    def set_high_limit(self, limit: float) -> None:
        if self.limited:
            value_string = self.pv + ".HLM"
            caput(value_string, limit)

    def set_low_limit(self, limit: float) -> None:
        if self.limited:
            value_string = self.pv + ".LLM"
            caput(value_string, limit)

    def set_limits(self, high: float, low: float) -> None:
        self.set_high_limit(limit=high)
        self.set_low_limit(limit=low)


@dataclass(slots=True)
class StringValuePV(PVModel):
    """Used to interact with PVs that work with strings."""

    readback: str = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        self._create_rbv_string()

        if self.monitor:
            object.__setattr__(
                self, "readback", caget(self._rbv_string, as_string=True)
            )
            camonitor(self._rbv_string, callback=self._monitor_pv)

    def _monitor_pv(self, **kwargs) -> None:
        object.__setattr__(self, "readback", kwargs["char_value"])
        object.__setattr__(self, "_moving", True)

    def move(self, value: str) -> None:
        """Moves the motor"""
        if not self.movable:
            return None

        if self.moving:
            return None

        caput(self.pv, value)
