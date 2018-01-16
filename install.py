#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Program docstring.
Installs SDCP
"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

from sys import argv, path as syspath

from json import load,dumps
syspath.insert(1, '../')
if len(argv) < 2:
 print "Usage: {} <json file>".format(argv[0])
 print "\n!!! Please import DB structure from mysql.txt before installing !!!\n"
 exit(0)
else:
 from os import path as ospath
 from sdcp.tools.installation import install
 settingsfilename = ospath.abspath(ospath.join(ospath.dirname(__file__),argv[1]))
 with open(settingsfilename) as settingsfile:
  settings = load(settingsfile)
 settings['source'] = settingsfilename
 res = install(settings)
 print dumps(res,indent=4)
 exit(0 if res.get('res') == 'OK' else 1)
