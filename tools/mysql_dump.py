#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"

#
#
if __name__ == "__main__":
 from sys import path as syspath, argv, exit, stdout
 if len(argv) < 3 or not argv[2] in ['-s','-d','-v','-r']:
  print(argv[0] + " <settings.json> -d(atabase)|-s(tructure)|-v(alues|-r(estore) [io-file]")
  exit(0)

 from os import path as ospath, getcwd
 syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..')))
 from rims.rest import mysql
 from rims.core.engine import Context

 ctx = Context(aConfigFile = argv[1])
 args = {}
 res = []
 if   argv[2] == '-d':
  args.update({'mode':'database','full':True})
  res = mysql.dump(args, ctx)
 elif argv[2] == '-v':
  args.update({'mode':'database','full':False})
  res = mysql.dump(args, ctx)
 elif argv[2] == '-s':
  args.update({'mode':'structure'})
  res = mysql.dump(args, ctx)
 elif argv[2] == '-r' and len(argv) == 4:
  args.update({'file':ospath.abspath(ospath.join(getcwd(),argv[3]))})
  res = mysql.restore(args, ctx)
 stdout.write("\n".join(res['output']))
