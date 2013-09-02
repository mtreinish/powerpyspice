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

import gtk
import h5py
import matplotlib.backends.backend_gtkagg as gtkagg
import matplotlib.figure
from oslo.config import cfg

from powerpyspice.hdf import spice_to_hdf
from powerpyspice import plot

CONF = cfg.CONF


class PyApp(gtk.Window):
    def __init__(self):
        super(PyApp, self).__init__()
        self.filename = None
        self.plot_dict = {}
        self.connect("destroy", gtk.main_quit)
        self.set_size_request(250, 150)
        self.set_position(gtk.WIN_POS_CENTER)
        self.mb = gtk.MenuBar()
        self.add_menu_bar()
        self.vbox = gtk.VBox(False, 2)
        self.vbox.pack_start(self.mb, False, False, 0)
        self.add(self.vbox)
        self.show_all()

    def add_menu_bar(self):
        # Add file menu
        filemenu = gtk.Menu()
        filem = gtk.MenuItem("_File")
        filem.set_submenu(filemenu)
        agr = gtk.AccelGroup()
        self.add_accel_group(agr)
        # Add open menu item
        openm = gtk.ImageMenuItem(gtk.STOCK_OPEN, agr)
        key, mod = gtk.accelerator_parse("<Control>O")
        openm.add_accelerator("activate", agr, key, mod, gtk.ACCEL_VISIBLE)
        openm.connect("activate", self.open_menu_widget)
        filemenu.append(openm)
        # Add exit menu item
        sep = gtk.SeparatorMenuItem()
        filemenu.append(sep)
        exit = gtk.ImageMenuItem(gtk.STOCK_QUIT, agr)
        key, mod = gtk.accelerator_parse("<Control>Q")
        exit.add_accelerator("activate", agr, key, mod, gtk.ACCEL_VISIBLE)
        exit.connect("activate", gtk.main_quit)
        # Append File Menu
        filemenu.append(exit)
        self.mb.append(filem)

    def open_menu_widget(self, *args, **kwargs):
        dialog = gtk.FileChooserDialog("Open..", None,
                                       gtk.FILE_CHOOSER_ACTION_OPEN,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)
        filter = gtk.FileFilter()
        filter.set_name("Input file")
        filter.add_pattern("*.h5")
        filter.add_pattern("*.raw")
        dialog.add_filter(filter)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            self.filename = dialog.get_filename()
        elif response == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
        dialog.destroy()
        self.hdf_file = self._get_hdf_file()
        self.select_plots()

    def _get_plots(self):
        return map(lambda x: x[0], self.hdf_file.items())

    def add_plot_on_click(self, path, model, *ignore):
        if path is not None:
            it = model.get_iter(path)
            model[it][0] = not model[it][0]

    def _toggle_check(self, widget, label):
        self.plot_dict[label] = not self.plot_dict[label]

    def _get_vector_names(self, plot_name):
        vector_names = []
        for vector in self.hdf_file.get(plot_name).values():
            if 'scale' not in vector.name:
                vector_names.append(vector.attrs['name'])
        return vector_names

    def select_plots(self):
        plots = self._get_plots()
        # Filename Label:
        hbox = gtk.HBox(homogeneous=True)
        hbox.pack_start(gtk.Label(self.filename))
        self.vbox.pack_start(hbox)
        hbox.show_all()
        # Display key
        hbox = gtk.HBox(homogeneous=True)
        hbox.pack_start(gtk.Label('Plot Name'))
        hbox.pack_start(gtk.Label('Selected'))
        hbox.pack_start(gtk.Label('Data Vectors'))
        self.vbox.pack_start(hbox)
        hbox.show_all()
        # Generate checkbox list for plots
        for i in plots:
            self.plot_dict[i] = False
            hbox = gtk.HBox(homogeneous=True)
            hbox.pack_start(gtk.Label(i))
            button = gtk.CheckButton("Selected")
            button.connect("toggled", self._toggle_check, i)
            hbox.pack_start(button)
            hbox.pack_start(gtk.Label(str(self._get_vector_names(i))))
            self.vbox.pack_start(hbox)
            hbox.show_all()
        # Generate plot toggle button
        button = gtk.Button("Display Plots")
        button.connect("clicked", self.display_plot, None)
        self.vbox.pack_start(button, False)
        button.show()

    def _get_enabled_plots(self):
        plots = []
        for i in self.plot_dict:
            if self.plot_dict[i]:
                plots.append(i)
        return plots

    def display_plot(self, *args, **kwargs):
        plots = self._get_enabled_plots()
        win = gtk.Window()
        win.connect("destroy", lambda x: gtk.main_quit())
        win.set_default_size(800, 600)
        win.set_title("Plot Window")
        vbox = gtk.VBox()
        win.add(vbox)
        fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        plot.display_plot(self.hdf_file, plots=plots, ax=ax)
        canvas = gtkagg.FigureCanvasGTKAgg(fig)
        vbox.pack_start(canvas)
        toolbar = gtkagg.NavigationToolbar2GTKAgg(canvas, win)
        vbox.pack_start(toolbar, False, False)
        win.show_all()

    def on_warn(self, message):
        md = gtk.MessageDialog(self, gtk.DIALOG_DESTROY_WITH_PARENT,
                               gtk.MESSAGE_WARNING, gtk.BUTTONS_CLOSE,
                               message)
        md.run()
        md.destroy

    def on_error(self, message):
        md = gtk.MessageDialog(self, gtk.DIALOG_DESTROY_WITH_PARENT,
                               gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE,
                               message)
        md.run()
        md.destroy()

    def _get_hdf_file(self):
        if self.filename is None:
            self.on_warn("A filename must be chosen")
        if self.filename.endswith('.h5'):
            return h5py.File(self.filename, "r")
        elif '.raw' in self.filename:
            hdf = spice_to_hdf.HdfCreate(self.filename)
            return h5py.File(hdf.outfile, "r")
        else:
            self.on_error("Unrecognized file extension for %s" % self.filename)
            return
