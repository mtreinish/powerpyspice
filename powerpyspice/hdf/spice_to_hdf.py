#!/usr/bin/env python

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

import h5py
from oslo.config import cfg

from powerpyspice import spice

CONF = cfg.CONF

hdf_cli_opts = [
    cfg.StrOpt('hdf-out-dir',
               short='d',
               default=None,
               help="Optional directory to store created hdf5 files. By"
               " default it will be put in your working directory"),
    cfg.StrOpt('hdf-file',
               short='o',
               default='spice.h5',
               help="Filename for hdf file created from spice raw."),
    cfg.BoolOpt('overwrite',
                default=False,
                help="Overwrite plot if it already exists in the hdf5 file"),
    cfg.StrOpt('title',
               short='t',
               default="Spice Plots",
               help="Specify a title to use for the plots and the hdf"
                    " metadata"),
]

CONF.register_cli_opts(hdf_cli_opts)


class HdfCreate(object):
    """Create hdf file from spice raw file

    This class is used to create or update an hdf5 file from a spice
    raw file.
    """
    def __init__(self, spice_file):
        self.spice_data = spice.SpiceReader(spice_file)
        self.plots = self.spice_data.get_plots()
        if CONF.hdf_out_dir:
            self.outfile = os.path.join(CONF.hdf_out_dir, CONF.hdf_file)
        else:
            self.outfile = CONF.hdf_file

        for index, plot in enumerate(self.plots):
            self.insert_spiceplot(plot, index)

    def insert_spiceplot(self, plot, index):
        ## Open the hdf5-file
        h5file = h5py.File(self.outfile, "a")
        unoriginal_plot_names = [
            "plotname undefined",
            "transient time domain plot",
        ]
        if plot.plotname in unoriginal_plot_names:
            name = "plot%s" % index
        else:
            name = plot.plotname
        # Create plot group and metadata
        group = h5file.create_group(name)
        group.attrs['id'] = index
        group.attrs['title'] = name
        group.attrs['date'] = plot.date
        group.attrs['name'] = plot.plotname
        group.attrs['plot_type'] = plot.plottype
        # Create the scale dataset and populate metadata
        scale = plot.get_scalevector()
        scale_data = scale.get_data()
        scale_dset = group.create_dataset('scale', data=scale_data)
        scale_dset.attrs['name'] = scale.name
        scale_dset.attrs['vtype'] = scale.type
        scale_dset.attrs['vlength'] = len(scale_data)
        # Create the data groups, tables and arrays
        for subindex, vdata in enumerate(plot.get_datavectors()):
            vdata_array = vdata.get_data()
            data_vector = group.create_dataset('data_vector-%s' % subindex,
                                               data=vdata_array)
            data_vector.attrs['id'] = subindex
            data_vector.attrs['name'] = vdata.name
            data_vector.attrs['vtype'] = vdata.type
            data_vector.attrs['vlength'] = len(vdata_array)
        h5file.flush()
        h5file.close()
