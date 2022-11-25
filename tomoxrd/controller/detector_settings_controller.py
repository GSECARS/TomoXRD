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

from tomoxrd.model import MainModel
from tomoxrd.widget import MainWidget


class DetectorSettingsController:

    def __init__(self, model: MainModel, widget: MainWidget) -> None:
        super(DetectorSettingsController, self).__init__()

        self._model = model
        self._widget = widget

        self._update_starting_values()
        self._connect_detector_settings_widgets()

    def _connect_detector_settings_widgets(self) -> None:
        self._widget.detector_settings.spin_tomo_x.valueChanged.connect(self._spin_tomo_x_value_changed)
        self._widget.detector_settings.spin_tomo_z.valueChanged.connect(self._spin_tomo_z_value_changed)
        self._widget.detector_settings.spin_xrd_x.valueChanged.connect(self._spin_xrd_x_value_changed)
        self._widget.detector_settings.spin_xrd_z.valueChanged.connect(self._spin_xrd_z_value_changed)
        self._widget.detector_settings.spin_detector_out.valueChanged.connect(self._spin_detector_out_value_changed)

    def _update_starting_values(self) -> None:
        """Updates the starting values for all the detector settings spin boxes."""
        self._widget.detector_settings.spin_tomo_x.setValue(self._model.detector_settings.tomo_x)
        self._widget.detector_settings.spin_tomo_z.setValue(self._model.detector_settings.tomo_z)
        self._widget.detector_settings.spin_xrd_x.setValue(self._model.detector_settings.xrd_x)
        self._widget.detector_settings.spin_xrd_z.setValue(self._model.detector_settings.xrd_z)
        self._widget.detector_settings.spin_detector_out.setValue(self._model.detector_settings.detector_out)

    def _spin_tomo_x_value_changed(self) -> None:
        """Updates the current tomo x value based on user input."""
        self._model.detector_settings.tomo_x = self._widget.detector_settings.spin_tomo_x.value()

    def _spin_tomo_z_value_changed(self) -> None:
        """Updates the current tomo z value based on user input."""
        self._model.detector_settings.tomo_z = self._widget.detector_settings.spin_tomo_z.value()

    def _spin_xrd_x_value_changed(self) -> None:
        """Updates the current xrd x value based on user input."""
        self._model.detector_settings.xrd_x = self._widget.detector_settings.spin_xrd_x.value()

    def _spin_xrd_z_value_changed(self) -> None:
        """Updates the current xrd z value based on user input."""
        self._model.detector_settings.xrd_z = self._widget.detector_settings.spin_xrd_z.value()

    def _spin_detector_out_value_changed(self) -> None:
        """Updates the current detector out value based on user input."""
        self._model.detector_settings.detector_out = self._widget.detector_settings.spin_detector_out.value()
