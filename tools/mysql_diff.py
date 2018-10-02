#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"
__version__ = "4.0GA"
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
 from zdcp.rest import mysql
 from zdcp.Settings import Settings
 from zdcp.core.engine import Context
 file = ospath.abspath(ospath.join(getcwd(),argv[1]))
 diffs= mysql.diff({'schema_file':file}, Context(Settings,None))
 print diffs['diffs']
 for line in diffs['output']:
  print line.rstrip('\n')
