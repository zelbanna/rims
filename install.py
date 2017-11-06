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
 from tools.installation import install
 with open(argv[1]) as settingsfile:
  settings = load(settingsfile)
 settings['file'] = str(argv[1])
 res = install(settings)
 print dumps(res,indent=4)
 exit(0 if res.get('res') == 'OK' else 1)
