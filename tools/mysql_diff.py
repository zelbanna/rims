#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"
__version__ = "18.05.31GA"
__status__ = "Production"

#
#
if __name__ == "__main__":
 from sys import path as syspath, argv, exit, stdout
 if len(argv) < 2:
  print argv[0] + " <db-struct-file-to-compare>"
  exit(0)

 from os import path as ospath, getcwd
 syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..')))
 from sdcp.rest import mysql
 file = ospath.abspath(ospath.join(getcwd(),argv[1]))
 diffs= mysql.diff({'file':file})
 print diffs['diffs']
 for line in diffs['output']:
  print line.rstrip('\n')
