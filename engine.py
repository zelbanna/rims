#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Program docstring.

ZDCP Engine

"""
__author__ = "Zacharias El Banna"
__version__ = "4.0GA"
__status__ = "Production"


from os import path as ospath
from sys import path as syspath, exit
basepath = ospath.abspath(ospath.join(ospath.dirname(__file__), '..'))
syspath.insert(1, basepath)
from zdcp.core.engine import start
start(40)
exit(1)
