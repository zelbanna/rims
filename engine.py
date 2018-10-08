#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Program docstring.

System engine

"""
__author__ = "Zacharias El Banna"
__version__ = "5.0GA"
__status__ = "Production"

from os import path as ospath
from sys import path as syspath, exit, setcheckinterval
basepath = ospath.abspath(ospath.join(ospath.dirname(__file__), '..'))
syspath.insert(1, basepath)
setcheckinterval(200)
from zdcp.core.engine import start
start(20)
exit(1)
