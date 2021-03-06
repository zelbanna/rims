#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"

from csv import reader
from os   import path as ospath
from sys  import path as syspath, argv, exit as sysexit
from json import load
syspath.insert(1,ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..')))
from rims.core.common import DB

if __name__ == "__main__":
 if len(argv) < 2:
  print(argv[0] + " <config-file> <inventory-file>")
  sysexit(0)


 with open(argv[1],'r') as config_file:
  config  = load(config_file)
 database = DB(config['database']['name'],config['database']['host'],config['database']['username'],config['database']['password'])
 with database as db:
  db.query("SELECT * FROM locations")
  locations = db.get_dict('name')
  for location in locations.values():
   print(location)
  with open(argv[2],'r', newline ='') as f:
   data = reader(f, delimiter=';', quotechar='"')
   for row in data:
    if row[0] and row[1] and row[4][0:3] != 'S/N':
     indata = {'description':row[0],'vendor':row[1],'model':row[2],'product':row[3],'purchase_order':row[9],'external_id':row[7],'receive_date':row[10],'comments':row[14],'license':0}
     indata['support_contract'] = 0 if row[5] == 'No' else 1
     indata['serial'] = row[4] if row[4] and row[4] != 'N/A' else 'NULL'
     try:
      db.insert_dict('inventory',indata)
     except Exception as err:
      print("%s => %s"%(str(err),";".join(row)))
    else:
     print("suspicious line => %s"%(";".join(row)))
 sysexit(0)
