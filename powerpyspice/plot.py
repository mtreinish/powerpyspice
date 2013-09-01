# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Copyright 2013 Matthew Treinish
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

import matplotlib.lines as lines
import matplotlib.pyplot
import matplotlib.text as mtext
import matplotlib.transforms as mtransforms
from oslo.config import cfg

CONF = cfg.CONF


cli_opts = [cfg.StrOpt('renderer',
            short='r',
            default="AGG",
            help="Specify the matplotlib render to use. This affects the"
                 " output format of the plot. The default is png use agg."),
            cfg.MultiStrOpt('plots',
            short='p',
            help="Name of plot to be plotted")]

CONF.register_cli_opts(cli_opts)


class SpiceLine(lines.Line2D):

    def __init__(self, *args, **kwargs):
        # we'll update the position when the line data is set
        self.text = mtext.Text(0, 0, '')
        super(SpiceLine, self).__init__(*args, **kwargs)

        # we can't access the label attr until *after* the line is
        # inited
        self.text.set_text(self.get_label())

    def set_figure(self, figure):
        self.text.set_figure(figure)
        lines.Line2D.set_figure(self, figure)

    def set_axes(self, axes):
        self.text.set_axes(axes)
        lines.Line2D.set_axes(self, axes)

    def set_transform(self, transform):
        # 2 pixel offset
        texttrans = transform + mtransforms.Affine2D().translate(2, 2)
        self.text.set_transform(texttrans)
        lines.Line2D.set_transform(self, transform)

    def set_data(self, x, y):
        if len(x):
            self.text.set_position((x[-1], y[-1]))

        lines.Line2D.set_data(self, x, y)

    def draw(self, renderer):
        # draw my label at the end of the line with 2 pixel offset
        lines.Line2D.draw(self, renderer)
        self.text.draw(renderer)


def display_plot(hdf_file, plots=None, ax=None):
    if plots is None:
        plots = CONF.plots
    for plot in plots:
        plot_to_graph = hdf_file.get(plot)
        x = None
        data_vectors = []
        for vector in plot_to_graph.values():
            if 'scale' in vector.name:
                x = vector[:]
            else:
                data_vectors.append(vector)
        if x is None:
            print "No scale vector was found in the hdf plot specified"
            exit(1)

        for vector in data_vectors:
            y = vector[:]
            if ax is None:
                matplotlib.pyplot.plot(x, y, label=vector.attrs['name'])
            else:
                ax.plot(x, y, label=vector.attrs['name'])
    if ax is None:
        matplotlib.pyplot.legend()
        matplotlib.pyplot.show()
