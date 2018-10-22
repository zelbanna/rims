#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" System engine """
__author__ = "Zacharias El Banna"

from os import path as ospath
from sys import path as syspath, argv
basepath = ospath.abspath(ospath.join(ospath.dirname(__file__), '..'))
syspath.insert(1, basepath)
from core.engine import run
if len(argv) < 2:
 aFile = 'config.json'
else:
 aFile = argv[1]
run(aFile)
