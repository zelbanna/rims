#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"
__version__ = "4.0GA"
__status__ = "Production"

#
#
if __name__ == "__main__":
 from sys import path as syspath, argv, exit,stdout
 if len(argv) < 2:
  print argv[0] + " [struct-file]"
  exit(0)
 else:
  from os import getcwd, path as ospath
  syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..')))
  from zdcp.rest import mysql 
  from zdcp.Settings import SC
  mysql.__add_globals__({'SC':SC})
  res = mysql.patch({"schema_file":ospath.abspath(ospath.join(getcwd(),argv[1]))})
  stdout.write("%s\n"%(res))
