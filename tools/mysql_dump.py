#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

#
#
if __name__ == "__main__":
 from sys import path as syspath, argv, exit
 if len(argv) < 2 or not argv[1] in ['-s','-d','-v','-r']:
  print argv[0] + " -d(atabase)|-s(tructure)|-v(alues|-r(estore) [restore-file]"
  exit(0)

 from os import path as ospath
 syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), '../..')))
 from sdcp import PackageContainer as PC
 from sdcp.core import mysql

 if   argv[1] == '-d':
  print "DROP DATABASE IF EXISTS {0};\nCREATE DATABASE {0};\nUSE {0};".format(PC.generic['db'])
  mysql.dump({'mode':'database','full':True})
 elif argv[1] == '-v':
  mysql.dump({'mode':'database','full':False})
 elif argv[1] == '-s':
  print "DROP DATABASE IF EXISTS {0};\nCREATE DATABASE {0};\nUSE {0};".format(PC.generic['db'])
  mysql.dump({'mode':'structure','file':ospath.join(PC.repo,'mysql.txt')})
 elif argv[1] == '-r' and len(argv) == 3:
  from os import  path as ospath, getcwd
  file = ospath.abspath(ospath.join(getcwd(),argv[2]))
  mysql.restore({'file':file})

