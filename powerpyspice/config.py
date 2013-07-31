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

from oslo.config import cfg
import pbr.version

version_info = pbr.version.VersionInfo('powerpyspice')
version_string = version_info.version_string


def parse_args(argv, default_config_files=None):
    cfg.CONF(argv[1:],
             project='power-pyspice',
             version=version_string,
             default_config_files=default_config_files)
