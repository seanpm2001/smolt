#!/usr/bin/python
# -*- coding: utf-8 -*-
# smolt - Fedora hardware profiler
#
# Copyright (C) 2007 Mike McGrath
# Copyright (C) 2010 Sebastian Pipping <sebastian@pipping.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA.

__requires__='TurboGears[future]'
import pkg_resources
#pkg_resources.require("TurboGears")

import threading

from turbogears import update_config, start_server
import cherrypy
cherrypy.lowercase_api = True
from os.path import *
import sys
from hardware.featureset import init, config_filename

_cfg_filename = None
if len(sys.argv) > 1:
    _cfg_filename = sys.argv[1]

init(_cfg_filename)
update_config(configfile=config_filename(),modulename="hardware.config")

from hardware.controllers import Root

thoo = threading.Thread(target=start_server, args=(Root(),))
thoo.start()
