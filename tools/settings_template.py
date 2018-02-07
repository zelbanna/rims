#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

from os   import path as ospath
from sys  import path as syspath
syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), '../..')))

if __name__ == "__main__":
 from sys import argv, exit
 if len(argv) < 2:
  print argv[0] + " <output file>"
  exit(0)

 from sdcp.core.dbase import DB
 config = {}
 with DB() as db:
  db.do("SELECT DISTINCT section FROM settings")
  sections = db.get_rows()
  for section in sections:
   sect = section['section']
   config[sect] = {}
   db.do("SELECT parameter,value,description,required FROM settings WHERE section = '%s' ORDER BY parameter"%sect)
   params = db.get_rows()
   for param in params:
    key = param.pop('parameter',None)
    if key in ['username', 'password', 'encrypted','url','domain']:
     param['value'] = key
    config[sect][key] = param
 try:
  from json import load,dump, dumps
  with open(argv[1],'w') as f:
   dump(config,f,indent=4,sort_keys=True)
 except:
  print "Error saving file"
  exit(1)
 else:
  print "Saved template file"
 exit(0)
