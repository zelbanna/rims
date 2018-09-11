#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"
__version__ = "4.0GA"
__status__ = "Production"

#
#
if __name__ == "__main__":
 from sys import path as syspath, argv, exit,stdout
 if len(argv) < 2 or not argv[1] in ['-s','-d','-v','-r']:
  print argv[0] + " -d(atabase)|-s(tructure)|-v(alues|-r(estore) [io-file]"
  exit(0)

 from os import path as ospath, getcwd
 syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..')))
 from zdcp.rest import mysql
 from zdcp.SettingsContainer import SC
 mysql.__add_globals__({'SC':SC})
 file = ospath.abspath(ospath.join(getcwd(),argv[2])) if len(argv) > 2 else None

 if   argv[1] == '-d':
  res = mysql.dump({'mode':'database','full':True})
 elif argv[1] == '-v':
  res = mysql.dump({'mode':'database','full':False})
 elif argv[1] == '-s':
  res = mysql.dump({'mode':'structure'})
 elif argv[1] == '-r' and len(argv) == 3:
  res = mysql.restore({'file':file})
 stdout.write("\n".join(res['output']))
