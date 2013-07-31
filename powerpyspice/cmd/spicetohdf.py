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

import sys

from oslo.config import cfg
import pbr.version

from powerpyspice import config
from powerpyspice.hdf import spice_to_hdf

CONF = cfg.CONF


def main():
    """Parse the options and call the appropriate class/methods."""
    print "running spice to hdf conversion"
    try:
        config.parse_args(sys.argv)
    except cfg.ConfigFilesNotFoundError:
        print("Could not read")
        return(2)

    if not CONF.version:
        print(pbr.version.VersionInfo('powerpyspice'))
        return(0)

    if not CONF.spicefile:
        print("You must specify a spice file to run this command:")
        return(1)

    hdf = spice_to_hdf.HdfCreate(CONF.spicefile)
    print "HDF file created sucessfully, it is located at:\n %s" % hdf.outfile
    return(0)
