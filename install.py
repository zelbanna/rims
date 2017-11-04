#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Program docstring.
Installs SDCP
"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

from sys import argv, path as syspath
syspath.insert(1, '../')
      
if len(argv) < 2:
 print "Usage: {} <json file>".format(argv[0])
 print "\n!!! Please import DB structure from mysql.txt before installing !!!\n"
 exit(0)
else:
 from tools.installation import install
 exit(install(argv[1]))
