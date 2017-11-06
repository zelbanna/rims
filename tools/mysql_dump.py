#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"


def db_structure():
 try:
  from subprocess import check_output
  from sdcp import PackageContainer as PC
  return check_output(['mysqldump','--no-data',"-u{}".format(PC.generic['dbuser']),"-p{}".format(PC.generic['dbpass']),PC.generic['db']])
 except Exception,e: 
  print "DumpError:{}".format(str(e))
 return ""

if __name__ == "__main__":
 from os import path as ospath
 from sys import path as syspath
 syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), '../..')))
 from sdcp import PackageContainer as PC
 print "USE {};".format(PC.generic['db'])
 for line in db_structure().split('\n'):
  if not line[:2] in [ '/*','--']:
   if "AUTO_INCREMENT=" in line:
    parts = line.split();
    for index, part in enumerate(parts):
     if "AUTO_INCREMENT=" in part:
      parts[index] = ''
    print " ".join(parts)
   else:
    print line
