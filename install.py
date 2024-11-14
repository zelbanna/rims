#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
""" Obsolete Installer

TODO
- assume DB is installed
- install devices and services from 'engine'
- if not master, detect this in engine and auto-register 

"""
__author__ = "Zacharias El Banna"
__version__ = "X.X"

from sys import path as syspath, exit as sysexit
from json import load,dumps
from os import chmod, listdir, path as ospath
from subprocess import check_call
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pip import main as pipmain
pkgdir = ospath.abspath(ospath.dirname(__file__))
basedir = ospath.abspath(ospath.join(pkgdir,'..'))
syspath.insert(1, basedir)
from rims.core.common import DB, rest_call
res = {'data':{},'info':{},'modules':{}}

parser = ArgumentParser(prog='install',formatter_class=RawDescriptionHelpFormatter,description="""RIMS installation

1) Set up config.json first - see example 'templates/config.json'
2) Then import database schema.db
3a) tools/mysql_tools </path/config json file> -r <schema>  (first time install)
3b) tools/mysql_tools </path/config json file> -p <schema>  (subsequent install)
""")
parser.add_argument('-c','--config', help = 'Config file',default = '/etc/rims/rims.json', required=False)
parsedinput = parser.parse_args()

if not parsedinput.config:
 parser.print_help()
 sysexit(0)

############################################### ALL #################################################
#
# load config
#
config = {}
config_file = ospath.abspath(parsedinput.config)
with open(config_file,'r') as sfile:
 config = load(sfile)
config['config_file'] = config_file
config['salt'] = config.get('salt','WBEUAHfO')

############################################ MASTER ###########################################
#
# Install necessary modules
#
if config['id'] == 'master':
 from importlib import import_module

 #
 # Device types
 #
 devdir = ospath.abspath(ospath.join(pkgdir,'devices'))
 device_types = []
 for file in listdir(devdir):
  pyfile = file[:-3]
  if file[-3:] == ".py" and pyfile[:2] != "__":
   try:
    mod = import_module(f'rims.devices.{pyfile}')
    tp = getattr(mod,'__type__',None)
    icon = getattr(mod,'__icon__','viz-generic.png')
    oid = getattr(mod,'__oid__',0)
    dev = getattr(mod,'Device',None)
    if tp:
     device_types.append({'name':pyfile, 'base':tp, 'functions':",".join(dev.get_functions()),'icon':icon,'oid':oid })
   except: pass
 res['data']['devices_found'] = len(device_types)
 res['data']['devices_new'] = 0

 #
 # Service types
 #
 srvdir = ospath.abspath(ospath.join(pkgdir,'api','services'))
 service_types = []
 for file in listdir(srvdir):
  pyfile = file[:-3]
  if file[-3:] == ".py" and pyfile[:2] != "__":
   try:
    mod = import_module(f'rims.api.services.{pyfile}')
    tp = getattr(mod,'__type__',None)
   except Exception as e:
    print('error',str(e))
   else:
    if tp:
     service_types.append({'service':pyfile, 'type':tp})
 res['data']['services_found'] = len(service_types)
 res['data']['services_new'] = 0

 #
 # Common config and user - for master...
 #
 from rims.api.mysql import diff, patch
 from hashlib import sha256
 try:
  settings = config['database']
  database,host,username,password = settings['name'],settings['host'],settings['username'],settings['password']
  db = DB(database,host,username,password)
  db.connect()
  passhash = sha256()
  passhash.update(b'changeme')
  passcode = passhash.hexdigest()
  res['data']['create_admin_user'] = (db.execute(f"INSERT users (id,name,alias,password,class) VALUES(1,'Administrator','admin','{passcode}','admin') ON DUPLICATE KEY UPDATE id = id, class='admin', password = '{passcode}'") > 0)
  res['data']['create_master_node'] = (db.execute(f"INSERT nodes (node,url) VALUES('{config['id']}','{config['master']}') ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)") > 0)
  res['data']['master_node_id']  = db.get_last_id()
  res['data']['create_generic_device'] = (db.execute("INSERT device_types (id,name,base) VALUES (0,'generic','generic') ON DUPLICATE KEY UPDATE id = 0") > 0)

  sql ="INSERT device_types (name,base,icon,functions,oid) VALUES ('%(name)s','%(base)s','images/%(icon)s','%(functions)s','%(oid)s') ON DUPLICATE KEY UPDATE oid = %(oid)s, icon = 'images/%(icon)s', functions = '%(functions)s'"
  for tp in device_types:
   try:    res['data']['devices_new'] += db.execute(sql%tp)
   except Exception as err: res['info']['devices'] = str(err)

  sql = "INSERT service_types (service,type) VALUES ('%(service)s','%(type)s') ON DUPLICATE KEY UPDATE id = id"
  for tp in service_types:
   try:   res['data']['services_new'] += db.execute(sql%tp)
   except Exception as err: res['info']['services'] = str(err)

  db.close()

 except Exception as e:
  print("Database error: %s"%str(e))

########################################### EXTRA NODES ############################################

else:
 try:
  res['data']['register'] = rest_call("%s/register"%config['master'], aHeader = {'X-Token':config.get('token')}, aArgs = {'id':config['id'],'port':config['port']})
 except Exception as e:
  res['info']['register'] = str(e)

res['status'] = 'OK' if not res['info'] else 'NOT_OK'

############################################### ALL #################################################
#
# End
#
print(dumps(res,indent=4,sort_keys=True))
sysexit(0 if res.get('status') == 'OK' else 1)
