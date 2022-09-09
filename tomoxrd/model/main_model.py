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

from tomoxrd.model import (
    PathModel,
    EpicsModel,
    BMDModel,
    ScanningModel,
)


@dataclass
class MainModel:
    """Base model class for TomoXRD"""

    settings: QSettings = field(init=True, repr=False, compare=False)

    paths: PathModel = field(init=False, repr=False, compare=False)
    epics: EpicsModel = field(init=False, repr=False, compare=False)
    bmd: BMDModel = field(init=False, repr=False, compare=False)
    scanning: ScanningModel = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "paths", PathModel())
        object.__setattr__(self, "epics", EpicsModel())
        object.__setattr__(self, "bmd", BMDModel())
        object.__setattr__(self, "scanning", ScanningModel())
