# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 Matthew Treinish
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
import sys

import h5py
from oslo.config import cfg
import pbr.version

from powerpyspice import config
from powerpyspice.hdf import spice_to_hdf
from powerpyspice import plot

CONF = cfg.CONF


def main():
    """Parse the options and call the appropriate class/methods."""
    try:
        config.parse_args(sys.argv)
    except cfg.ConfigFilesNotFoundError:
        print("Could not read.")
        return(2)

    if not CONF.version:
        print(pbr.version.VersionInfo('powerpyspice'))
        return(0)

    if CONF.spicefile:
        # TODO(mtreinish) This will create a hdf file and then close it
        # however we will use it again right after creation so this should
        # be reworked so that it's not closed until plotting is finished
        hdf = spice_to_hdf.HdfCreate(CONF.spicefile)
        h5file = hdf.outfile
    else:
        if CONF.hdf_out_dir:
            h5file = os.path.join(CONF.hdf_out_dir, CONF.hdf_file)
        else:
            h5file = CONF.hdf_file

    hdf_file = h5py.File(h5file, "r")
    plot.display_plot(hdf_file)
