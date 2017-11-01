#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"
__version__ = "1.1GA"
__status__ = "Production"

from os import path as ospath
from sys import path as syspath
syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), '..')))

import PackageContainer as PC

try:
 from subprocess import check_output
 mysql = check_output(['mysqldump','--no-data',"-u{}".format(PC.generic['dbuser']),"-p{}".format(PC.generic['dbpass']),PC.generic['db']])
 for line in mysql.split('\n'):
  if not line[:2] in [ '/*','--']:
   print line
except Exception,e: 
 print str(e)
