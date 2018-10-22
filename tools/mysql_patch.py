#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"

#
#
if __name__ == "__main__":
 from sys import path as syspath, argv, exit,stdout
 if len(argv) < 3:
  print(argv[0] + " <settings.json> [struct-file]")
  exit(0)
 else:
  from os import getcwd, path as ospath
  syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..')))
  from rims.rest import mysql
  from rims.core.engine import Context
  args = {"schema_file":ospath.abspath(ospath.join(getcwd(),argv[2]))}
  res = mysql.patch(args,Context(aConfigFile = argv[1]))
  stdout.write("%s\n"%(res))
