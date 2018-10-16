#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"
__version__ = "5.3GA"
__status__ = "Production"

#
#
if __name__ == "__main__":
 from sys import path as syspath, argv, exit, stdout
 if len(argv) < 2:
  print(argv[0] + " <settings.json> <db-struct-file-to-compare>")
  exit(0)

 from os import path as ospath, getcwd
 syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..')))
 from zdcp.rest import mysql
 from zdcp.core.engine import Context
 from json import load
 with open(argv[1],'r') as f:
  settings = load(f)
 args = {"schema_file":ospath.abspath(ospath.join(getcwd(),argv[2]))}
 args['database'] = settings['system']['db_name']
 args['username'] = settings['system']['db_user']
 args['password'] = settings['system']['db_pass']


 diffs= mysql.diff(args, Context({'system':{'id':None}},None))
 print(diffs['diffs'])
 for line in diffs['output']:
  print(line.rstrip('\n'))
