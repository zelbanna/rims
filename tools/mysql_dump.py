#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"
__version__ = "5.1GA"
__status__ = "Production"

#
#
if __name__ == "__main__":
 from sys import path as syspath, argv, exit,stdout
 if len(argv) < 3 or not argv[2] in ['-s','-d','-v','-r']:
  print(argv[0] + " <settings.json> -d(atabase)|-s(tructure)|-v(alues|-r(estore) [io-file]")
  exit(0)

 from os import path as ospath, getcwd
 syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..')))
 from zdcp.rest import mysql
 from zdcp.core.engine import Context

 ctx = Context({'system':{'id':None}},None)
 from json import load
 with open(argv[1],'r') as f:
  settings = load(f)
 args = {}
 args['database'] = settings['system']['db_name']['value']
 args['username'] = settings['system']['db_user']['value']
 args['password'] = settings['system']['db_pass']['value']

 if   argv[2] == '-d':
  args.update({'mode':'database','full':True})
  res = mysql.dump(args, ctx)
 elif argv[2] == '-v':
  args.update({'mode':'database','full':False})
  res = mysql.dump(args, ctx)
 elif argv[2] == '-s':
  args.update({'mode':'structure'})
  res = mysql.dump(args, ctx)
 elif argv[2] == '-r' and len(argv) == 3:
  args.update({'file':ospath.abspath(ospath.join(getcwd(),argv[3]))})
  res = mysql.restore(args, ctx)
 stdout.write("\n".join(res['output']))
