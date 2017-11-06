#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"


def db_dump(aDict):
 try:
  from subprocess import check_output
  from sdcp import PackageContainer as PC
  mode = aDict.get('mode','structure')
  cmd  = ["mysqldump", "-u{}".format(PC.generic['dbuser']), "-p{}".format(PC.generic['dbpass']), PC.generic['db']]
  if   mode == 'structure':
   cmd.append('--no-data')
  elif mode == 'database':
   cmd.extend(['-c','--skip-extended-insert'])
  return check_output(cmd)
 except Exception,e: 
  print "DumpError:{}".format(str(e))
 return ""

if __name__ == "__main__":
 from sys import path as syspath, argv, exit
 if len(argv) < 2 or not argv[1] in ['-s','-d']:
  print argv[0] + " -d(atabase)|-s(tructure)"
  exit(0)

 from os import path as ospath
 syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), '../..')))
 from sdcp import PackageContainer as PC
 print "USE {};".format(PC.generic['db'])

 if argv[1] == '-d':
  mode = 'database'
 else:
  mode = 'structure'

 for line in db_dump({'mode':mode}).split('\n'):
  if not line[:2] in [ '/*','--']:
   if "AUTO_INCREMENT=" in line:
    parts = line.split();
    for index, part in enumerate(parts):
     if "AUTO_INCREMENT=" in part:
      parts[index] = ''
    print " ".join(parts)
   else:
    print line
