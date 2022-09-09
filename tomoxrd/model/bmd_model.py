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
from typing import List, Optional

from tomoxrd.model import PVModel, DoubleValuePV, StringValuePV, EpicsConfig


@dataclass(frozen=True)
class BMDModel:

    detector_x: DoubleValuePV = field(init=False, repr=False, compare=False)
    detector_z: DoubleValuePV = field(init=False, repr=False, compare=False)

    collection: List[PVModel] = field(
        init=False, repr=False, compare=False, default_factory=lambda: []
    )

    def __post_init__(self) -> None:
        self._set_stages()

    def _add_pv(
        self,
        pv_name: str,
        movable: bool,
        limited: bool,
        rbv_extension: bool,
        monitor: Optional[bool] = False,
        as_string: Optional[bool] = False,
    ) -> None:

        name = pv_name
        if "_" in name:
            name.replace("_", " ")

        if as_string:
            pv_type = StringValuePV
        else:
            pv_type = DoubleValuePV

        object.__setattr__(
            self,
            pv_name,
            pv_type(
                name=name,
                pv=EpicsConfig[pv_name].value,
                movable=movable,
                limited=limited,
                rbv_extension=rbv_extension,
                monitor=monitor,
            ),
        )
        self.collection.append(getattr(self, pv_name))

    def _set_stages(self) -> None:
        # Stages
        self._add_pv(
            pv_name="detector_x",
            movable=True,
            limited=True,
            rbv_extension=True,
            monitor=True,
        )
        self._add_pv(
            pv_name="detector_z",
            movable=True,
            limited=True,
            rbv_extension=True,
            monitor=True,
        )
