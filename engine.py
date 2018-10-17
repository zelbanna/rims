#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" System engine """
__author__ = "Zacharias El Banna"
__version__ = "5.4"
__status__ = "Production"

from os import path as ospath
from sys import path as syspath, argv
basepath = ospath.abspath(ospath.join(ospath.dirname(__file__), '..'))
syspath.insert(1, basepath)
from zdcp.core.engine import run
if len(argv) < 2:
 aFile = 'settings.json'
else:
 aFile = argv[1]
run(aFile)
