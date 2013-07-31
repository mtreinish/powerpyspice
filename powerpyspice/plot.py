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

import matplotlib
#import numpy
from oslo.config import cfg

CONF = cfg.CONF


cli_opts = [cfg.StrOpt('renderer',
            short='r',
            default="AGG",
            help="Specify the matplotlib render to use. This affects the"
                 " output format of the plot. The default is png use agg.")]

CONF.register_cli_opts(cli_opts)

matplotlib.use(CONF.renderer)
