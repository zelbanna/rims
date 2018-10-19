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
  from zdcp.rest import mysql
  from zdcp.core.engine import Context
  from json import load
  with open(argv[1],'r') as f:
   settings = load(f)
  args = {"schema_file":ospath.abspath(ospath.join(getcwd(),argv[2]))}
  args['database'] = settings['system']['db_name']aWeb['node']
  args['username'] = settings['system']['db_user']aWeb['node']
  args['password'] = settings['system']['db_pass']aWeb['node']
  res = mysql.patch(args,Context({'system':{'id':None}}))
  stdout.write("%s\n"%(res))
