# vim: tabstop=4 shiftwidth=4 softtabstop=4

#     Copyright (C) 2007,2011 Werner Hoch
#     Copyright 2013 Matthew Treinish
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import numpy
import string

from oslo.config import cfg

from powerpyspice import exceptions

spice_file_opts = [
    cfg.BoolOpt('little-endian',
                default=False,
                help="Specify whether the system used to generate the"
                "waveforms used little-endian"),
    cfg.BoolOpt('double-precision',
                default=False,
                help="Specify whether the spice raw files using double"
                "recesion floats"),
    cfg.StrOpt('spicefile',
               short='i',
               help="The input spice raw files to be read in for "
                    "plotting"),
]
CONF = cfg.CONF
CONF.register_cli_opts(spice_file_opts)


class spice_vector(object):
    """
    Contains a single spice vector with it's data and it's attributes.
    The vector is numpy.array, either real or complex.
    The attributes are:
      * name: vector name
      * type: frequency, voltage or current
    """
    def __init__(self, vector=numpy.array([]), **kwargs):
        self.data = vector
        self.name = ""
        self.type = ""
        self.set_attributes(**kwargs)

    def set_attributes(self, **kwargs):
        """
        Set the attribues of the vector "name" and "type"
        """
        for k, v in kwargs.items():
            if hasattr(self, k):
                if type(getattr(self, k)) == type(v):
                    setattr(self, k, v)
                else:
                    print "Warning: attribute has wrong type: " \
                          + type(v) + " ignored!"
            else:
                print "Warning: unknown attribute" + k + " Ignored!"

    def set_data(self, data_array):
        """
        set a new numpy.array as data vector
        """
        self.data = data_array

    def get_data(self):
        """
        returns the data vector as numpy.array
        """
        return self.data


class spice_plot(object):
    """
    This class holds a single spice plot
    It contains one scale vector and a list of several data vectors.
    The plot may have some attributes like "title", "date", ...
    """
    def __init__(self, scale=None, data=None, **kwargs):
        """
        Initialize a new spice plot.
        Scale may be an spice_vector and data may be a list of spice_vectors.
        The attributes are provided by **kwargs.
        """
        self.title = "title undefined"
        self.date = "date undefined"
        self.plotname = "plotname undefined"
        self.plottype = "plottype undefined"
        self.dimensions = []

        ## a single scale vector
        if scale is None:
            scale = numpy.array([])
        else:
            self.scale_vector = scale

        ## init the list of spice_vector
        if data is None:
            self.data_vectors = []
        else:
            self.data_vectors = data

        self.set_attributes(**kwargs)

    def set_attributes(self, **kwargs):
        """
        Set the attributes of a plot.
        """
        for k, v in kwargs.items():
            if hasattr(self, k):
                if type(getattr(self, k)) == type(v):
                    setattr(self, k, v)
                else:
                    print "Warning: attribute has wrong type: " \
                          + type(v) + " ignored!"
            else:
                print "Warning: unknown attribute \"" + k + "\". Ignored!"

    def set_scalevector(self, spice_vector):
        """
        Set a spice_vector as the scale_vektor.
        """
        self.scale_vector = spice_vector

    def set_datavectors(self, spice_vector_list):
        """
        Set a list of spice_vector as data of spice_plot
        """
        self.data_vectors = spice_vector_list

    def append_datavector(self, spice_vector):
        """
        Append a single spice_vector to the data section
        """
        self.data_vectors.append(spice_vector)

    def get_scalevector(self):
        """
        returns the scale vector as a spice_vector
        """
        return self.scale_vector

    def get_datavector(self, n):
        """
        returns the n-th data vector as a spice_vector
        """
        return self.data_vectors[n]

    def get_datavectors(self):
        """
        return a list of all spice_vectors of the plot
        """
        return self.data_vectors


class SpiceReader(object):
    """
    This class is reads a spice data file and returns a list of spice_plot
    objects.

    The file syntax is mostly taken from the function raw_write() from
    ngspice-rework-17 file ./src/frontend/rawfile.c
    """

    def __init__(self, filename):
        self.plots = []
        self.set_default_values()
        self.readfile(filename)

    def set_default_values(self):
        ## Set the default values for some options
        self.current_plot = spice_plot()
        self.nvars = 0
        self.npoints = 0
        self.numdims = 0
        self.padded = True
        self.real = True
        self.vectors = []

    def readfile(self, filename):
        spice_file = open(filename, "rb")
        while True:
            line = spice_file.readline()
            if line == "":
                return
            tok = [string.strip(t) for t in string.split(line, ":", 1)]
            keyword = tok[0].lower()

            if keyword == "title":
                self.current_plot.set_attributes(title=tok[1])
            elif keyword == "date":
                self.current_plot.set_attributes(date=tok[1])
            elif keyword == "plotname":
                self.current_plot.set_attributes(plotname=tok[1])
            elif keyword == "flags":
                ftok = [string.lower(string.strip(t))
                        for t in string.split(tok[1])]
                for flag in ftok:
                    if flag == "real":
                        self.real = True
                    elif flag == "complex":
                        self.real = False
                    elif flag == "unpadded":
                        self.padded = False
                    elif flag == "padded":
                        self.padded = True
                    else:
                        print 'Warning: unknown flag: "' + flag + '"'
            elif keyword == "no. variables":
                self.nvars = string.atoi(tok[1])
            elif keyword == "no. points":
                self.npoints = string.atoi(tok[1])
            elif keyword == "dimensions":
                if self.npoints == 0:
                    print 'Error: misplaced "Dimensions:" lineprint'
                    continue
                print 'Warning: "Dimensions" not supported yet'
                # FIXME: How can I create such simulation files?
                # numdims = string.atoi(tok[1])
            elif keyword == "command":
                print 'Warning: "command" option not implemented yet'
                print '\t' + line
                # FIXME: what is this command good for
            elif keyword == "option":
                print 'Warning: "option" not implemented yet'
                print '\t' + line
                # FIXME: what is this command good for
            elif keyword == "variables":
                for i in xrange(self.nvars):
                    line = string.split(string.strip(spice_file.readline()))
                    if len(line) >= 3:
                        curr_vector = spice_vector(name=line[1],
                                                   type=line[2])
                        self.vectors.append(curr_vector)
                        if len(line) > 3:
                            print "warning can't handle variable details:"
                            print "Attributes: ", line[3:]
                            # min=, max, color, grid, plot, dim
                            # I think only dim is useful and neccesary
                    else:
                        print "list of variables is to short"

            elif keyword in ["values", "binary"]:
                if not CONF.double_precision:
                    data_type = numpy.dtype('float32')
                    binary_length = self.nvars * self.npoints * 4
                else:
                    data_type = numpy.dtype('float64')
                    binary_length = self.nvars * self.npoints * 8
                if not CONF.little_endian:
                    data_type = data_type.newbyteorder('>')
                if self.real:
                    if keyword == "values":
                        length = self.npoints * self.nvars
                        i = 0
                        a = numpy.zeros(length,
                                        dtype=data_type)
                        while (i < length):
                            t = string.split(spice_file.readline(), "\t")
                            if len(t) < 2:
                                continue
                            else:
                                a[i] = string.atof(t[1])
                            i += 1
                    else:
                        data = spice_file.read(binary_length)
                        array = numpy.frombuffer(data, dtype=data_type)
                    aa = array.reshape(self.npoints, self.nvars)
                    self.vectors[0].set_data(aa[:, 0])
                    self.current_plot.set_scalevector(self.vectors[0])
                    for n in xrange(1, self.nvars):
                        self.vectors[n].set_data(aa[:, n])
                        self.current_plot.append_datavector(self.vectors[n])
                # Complex number
                else:
                    if keyword == "values":
                        i = 0
                        a = numpy.zeros(self.npoints * self.nvars * 2,
                                        dtype=data_type)
                        while (i < self.npoints * self.nvars * 2):
                            t = string.split(spice_file.readline(), "\t")
                            if len(t) < 2:
                                continue
                            else:
                                t = string.split(t[1], ",")
                                a[i] = string.atof(t[0])
                                i += 1
                                a[i] = string.atof(t[1])
                                i += 1
                    else:
                        a = numpy.frombuffer(
                            spice_file.read(binary_length * 2),
                            dtype=data_type)
                    aa = a.reshape(self.npoints, self.nvars * 2)
                    # Only the real part:
                    self.vectors[0].set_data(aa[:, 0])
                    self.current_plot.set_scalevector(self.vectors[0])
                    for n in xrange(1, self.nvars):
                        self.vectors[n].set_data(
                            numpy.array(aa[:, 2 * n] + 1j * aa[:, 2 * n + 1]))
                        self.current_plot.append_datavector(self.vectors[n])

                # Create a new plot after the data
                self.plots.append(self.current_plot)
                self.set_default_values()

            elif string.strip(keyword) == "":
                continue

            else:
                msg = "Unexpected line in rawfile:\n" + line + "\nload aborted"
                raise exceptions.InvalidRawFile(msg)

    def get_plots(self):
        return self.plots
