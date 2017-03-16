#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Program docstring.

Site Application

"""
__author__ = "Zacharias El Banna"
__version__ = "1.0GA"
__status__ = "Production"

from sys import path as syspath
syspath.insert(1, "/usr/local/sbin")
from sdcp.site.www import Web

web = Web(aDebug = True)
web.site_start()
