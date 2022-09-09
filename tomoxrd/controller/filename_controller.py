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
import collections
import os
import shutil
import numpy as np
from epics import caget
from cryio import cbfimage, esperanto, crysalis

from tomoxrd.widget import MainWidget


class CBFNotFoundError(Exception):

    def __init__(self, msg) -> None:
        super(CBFNotFoundError, self).__init__()
        self.msg = msg


class FilenameController:
    # PVs
    _tiff_file_number: str = "13PIL1MCdTe:TIFF1:FileNumber"
    _tiff_file_name: str = "13PIL1MCdTe:TIFF1:FileName"
    _tiff_file_path: str = "13PIL1MCdTe:TIFF1:FilePath"
    _base_path: str = "T:/dac_user/2022/BMD_2022-3/Tomo"

    # File paths
    _set_filepath: str = "T:/dac_user/Setup/Crysalis/pilatus_1m.set"
    _ccd_filepath: str = "T:/dac_user/Setup/Crysalis/pilatus_1m.ccd"
    _par_filepath: str = "T:/dac_user/Setup/Crysalis/pilatus_1m_TOMO_37keV.par"

    _scans = collections.OrderedDict()
    starting_frame: int = 1

    def __init__(self, widget: MainWidget) -> None:
        self._widget = widget

        current_user_path = caget(self._tiff_file_path, as_string=True).replace("/DAC", self._base_path)
        if current_user_path[-1] != "/":
            current_user_path += "/"
        self._widget.filename_settings.ipt_path.setText(current_user_path)
        self._widget.filename_settings.flb_path.target_directory = self._base_path
        self._widget.filename_settings.flb_calibration.target_directory = self._base_path
        self._widget.filename_settings.lbl_calibration_path.setText(self._par_filepath.split("/")[-1])

        self._scans[0] = [
            {
                "count": 10,
                "omega": 0,
                "omega_start": 0.0,
                "omega_end": 5.0,
                "pixel_size": 0.172,
                "omega_runs": None,
                "theta": 0,
                "kappa": 0,
                "phi": 0,
                "domega": 0.5,
                "dtheta": 0,
                "dkappa": 0,
                "dphi": 0,
                "center_x": 525,
                "center_y": 514,
                "alpha": 50,
                "dist": 206.32,
                "l1": 0.2952,
                "l2": 0.2952,
                "l12": 0.2952,
                "b": 0.2952,
                "mono": 0.99,
                "monotype": 'SYNCHROTRON',
                "chip": [1044, 1044],
                "Exposure_time": 0.5,
            }
        ]

        self._connect_filename_settings_widgets()
        self._update_with_current_values()

    def _update_with_current_values(self) -> None:
        """
        Reads the current PV values for the file path and number
        and updates the widgets.
        """
        file_number = caget(self._tiff_file_number)
        file_name = caget(self._tiff_file_name, as_string=True)

        self._widget.filename_settings.ipt_filename.setText(file_name)
        self._widget.filename_settings.spin_frame_number.setValue(file_number)

    def _connect_filename_settings_widgets(self) -> None:
        self._widget.filename_settings.ipt_filename.returnPressed.connect(self._update_file_name)
        self._widget.filename_settings.ipt_path.returnPressed.connect(self._update_file_path)
        self._widget.filename_settings.flb_path.folder_path_changed.connect(self._change_existing_path)
        self._widget.filename_settings.flb_calibration.file_path_changed.connect(self._par_file_path_changed)

    def _par_file_path_changed(self, state: bool) -> None:
        if state:
            new_par_path = self._widget.filename_settings.flb_calibration.file_path
            self._par_filepath = new_par_path
            self._widget.filename_settings.lbl_calibration_path.setText(new_par_path.split("/")[-1])

    def _update_file_name(self) -> None:
        filename = self._widget.filename_settings.ipt_filename.text()

        invalid = '<>"/\\|?*#& '
        for char in invalid:
            filename = filename.replace(char, "_")

        self._widget.filename_settings.ipt_filename.setText(filename)

    def _update_file_path(self) -> None:
        filepath = self._widget.filename_settings.ipt_path.text()

        invalid = '<>"\\|?*#& '
        for char in invalid:
            filepath = filepath.replace(char, "_")

        if filepath[-1] != "/":
            filepath += "/"

        if not os.path.exists(filepath):
            os.makedirs(filepath)

        self._widget.filename_settings.ipt_path.setText(filepath)

    def _change_existing_path(self, state: bool) -> None:
        if state:
            current_path = self._widget.filename_settings.flb_path.folder_path
            if current_path[-1] != "/":
                current_path += "/"
            self._widget.filename_settings.ipt_path.returnPressed.disconnect()
            self._widget.filename_settings.ipt_path.setText(current_path)
            self._widget.filename_settings.ipt_path.returnPressed.connect(self._update_file_path)

    @staticmethod
    def create_esperanto_directory(filepath: str, filename: str) -> None:
        target_directory = os.path.join(filepath, f"{filename}_crys").replace("\\", "/")

        if not os.path.exists(target_directory):
            os.makedirs(target_directory)

    def create_par_file(self, filepath: str, filename: str) -> None:
        target_directory = os.path.join(filepath, f"{filename}_crys").replace("\\", "/")
        par_file = os.path.join(target_directory, filename + ".par").replace("\\", "/")

        with open(par_file, "w") as pf:
            with open(self._par_filepath, "r") as calf:
                for line in calf:
                    if line.startswith("FILE CHIP"):
                        pf.write(f"FILE CHIP {filename}.ccd\n")
                    else:
                        pf.write(line)

    def copy_set_and_ccd_files(self, filepath: str, filename: str) -> None:
        target_directory = os.path.join(filepath, f"{filename}_crys").replace("\\", "/")
        shutil.copy(self._set_filepath, os.path.join(target_directory, f"{filename}.set")).replace("\\", "/")
        shutil.copy(self._ccd_filepath, os.path.join(target_directory, f"{filename}.ccd")).replace("\\", "/")

    @staticmethod
    def convert_to_square(images_array: np.ndarray) -> np.ndarray:
        a = np.empty((1043, 31), dtype=images_array.dtype)
        b = np.empty((1043, 32), dtype=images_array.dtype)
        a.fill(-1)
        b.fill(-1)

        converted_images = np.hstack((b, np.hstack((images_array, a))))

        c = np.empty((1, 1044), dtype=images_array.dtype)
        c.fill(-1)

        return np.vstack((converted_images, c))

    def prepare_for_crysalis(
            self,
            num_angles: int,
            start: float,
            end: float,
            step: float,
            exposure: float,
    ) -> None:

        self._scans[0][0]["count"] = num_angles
        self._scans[0][0]["omega_start"] = start
        self._scans[0][0]["omega_end"] = end
        self._scans[0][0]["domega"] = step
        self._scans[0][0]["Exposure_time"] = exposure

    def convert_to_esperanto(
            self,
            filepath: str,
            filename: str,
            num_angles: int,
    ) -> None:
        target_directory = os.path.join(filepath, f"{filename}_crys").replace("\\", "/")

        for i in range(int(self.starting_frame - 1), int(self.starting_frame + num_angles - 1), 1):
            cbf_file = os.path.join(filepath, filename + "_{0:04d}".format(i + 1) + ".cbf").replace("\\", "/")
            esperanto_file = os.path.join(target_directory, f"{filename}_1_{i + 1}.esperanto").replace("\\", "/")

            try:
                if not os.path.exists(cbf_file):
                    raise CBFNotFoundError(f"[CBF-Error] - {cbf_file} does not exist!")
            except CBFNotFoundError as error:
                print(error.msg)
            else:
                trans_image = np.flip(cbfimage.CbfImage(cbf_file).array, 0)
                eps_target_image = self.convert_to_square(trans_image)

                kwargs = self._scans[0][0]
                kwargs['omega'] = kwargs['omega_start'] + kwargs['domega'] * i

                esperanto.EsperantoImage().save(esperanto_file, eps_target_image, **kwargs)

    def create_crysalis_exp_settings_file(self, filepath: str, filename: str) -> None:

        target_directory = os.path.join(filepath, f"{filename}_crys").replace("\\", "/")

        run_header = crysalis.RunHeader(filename.encode(), target_directory.encode(), 1)
        run_name = os.path.join(target_directory, filename).replace("\\", "/")
        run_file = []

        for omega_run in self._scans[0]:
            dscr = crysalis.RunDscr(0)
            dscr.axis = crysalis.SCAN_AXIS['OMEGA']
            dscr.kappa = omega_run['kappa']
            dscr.omegaphi = 0
            dscr.start = omega_run['omega_start']
            dscr.end = omega_run['omega_end']
            dscr.width = omega_run['domega']
            dscr.todo = dscr.done = omega_run['count']
            dscr.exposure = 1
            run_file.append(dscr)

        crysalis.saveRun(run_name, run_header, run_file)
        crysalis.saveCrysalisExpSettings(target_directory)
