#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Installer"""
__author__ = "Zacharias El Banna"
__version__ = "6.0"

from sys import argv, stdout, path as syspath
from json import load,dump,dumps
from os import remove, chmod, listdir, path as ospath
from subprocess import check_call
pkgdir = ospath.abspath(ospath.dirname(__file__))
basedir = ospath.abspath(ospath.join(pkgdir,'..'))
syspath.insert(1, basedir)
from rims.core.common import DB, rest_call
res = {'data':{},'info':{}}

if len(argv) < 2:
 print("Usage: %s </path/json file>\n"%argv[0])
 print("1) Set up config.json first - see example 'templates/config.json'")
 print("2) Then import database schema.db")
 print("3a) tools/mysql_dumps </path/json file> -r schema.db  (first time install)")
 print("3b) tools/mysql_patch </path/json file> schema.db     (subsequent install)")
 print("\nAlso, it is good to use github project log2ram for various purposes, foremost debug logging but also influxdb et al..")
 exit(0)
else:
 config_filename = argv[1]

############################################### ALL #################################################
#
# load config
#
config = {}
config_file = ospath.abspath(config_filename)
with open(config_file,'r') as sfile:
 config = load(sfile)
config['config_file'] = config_file
config['salt'] = config.get('salt','WBEUAHfO')

############################################### ALL #################################################
#
# Write engine operations files
#
with open(ospath.abspath(ospath.join(pkgdir,'templates',config['template'])),'r') as f:
 template = f.read()
template = template.replace("%PKGDIR%",pkgdir)
template = template.replace("%CFGFILE%",config_file)
engine_run = ospath.abspath(ospath.join(pkgdir,config['template']))
with open(engine_run,'w+') as f:
 f.write(template)
chmod(engine_run,0o755)
res['data']['engine']= {'template':config['template'],'install':check_call([engine_run,"install"])}

############################################### ALL #################################################
#
# Modules
#
try:
 from pip import main as pipmain
except:
 from pip._internal import main as pipmain
try: import pymysql
except ImportError:
 res['info']['pymysql'] = 'installing'
 pipmain(["install", "-q","pymysql"])
try: import dns
except ImportError:
 res['info']['dns'] = 'installing'
 pipmain(["install", "-q","dnspython"])
try: import paramiko
except ImportError:
 res['info']['ssh'] = 'installing'
 pipmain(["install", "-q","paramiko"])
try: import git
except ImportError:
 res['info']['git'] = 'installing'
 pipmain(["install","-q","gitpython"])
try: import pyVmomi
except ImportError:
 res['info']['pyVmomi'] = 'installing'
 pipmain(["install","-q","pyVmomi"])
try: import netsnmp
except ImportError:
 res['info']['netsnmp'] = 'installing'
 pipmain(["install","-q","python3-netsnmp"])
try: import jnpr.junos
except ImportError:
 res['info']['junos-eznc'] = 'installing'
 pipmain(["install","-q","junos-eznc"])

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
    mod = import_module("rims.devices.%s"%(pyfile))
    type = getattr(mod,'__type__',None)
    icon = getattr(mod,'__icon__','viz-generic.png')
    oid = getattr(mod,'__oid__',0)
    dev = getattr(mod,'Device',None)
    if type:
     device_types.append({'name':pyfile, 'base':type, 'functions':",".join(dev.get_functions()),'icon':icon,'oid':oid })
   except: pass
 res['data']['devices_found'] = len(device_types)
 res['data']['devices_new'] = 0

 #
 # Service types
 #
 srvdir = ospath.abspath(ospath.join(pkgdir,'api'))
 service_types = []
 for file in listdir(srvdir):
  pyfile = file[:-3]
  if file[-3:] == ".py" and pyfile[:2] != "__":
   try:
    mod = import_module("rims.api.%s"%(pyfile))
    type = getattr(mod,'__type__',None)
   except: pass
   else:
    if type:
     service_types.append({'service':pyfile, 'type':type})
 res['data']['services_found'] = len(service_types)
 res['data']['services_new'] = 0

 #
 # Common config and user - for master...
 #
 from rims.api import mysql
 from crypt import crypt
 try:
  database,host,username,password = config['database']['name'],config['database']['host'],config['database']['username'],config['database']['password']
  database_args = {'host':host,'username':username,'password':password,'database':database,'schema_file':ospath.join(pkgdir,'schema.db')}
  res['data']['database']= {}
  res['data']['database']['diff'] = mysql.diff(None, database_args)
  if res['data']['database']['diff']['diffs'] > 0:
   res['data']['database']['patch'] = mysql.patch(None, database_args)
   if res['data']['database']['patch']['status'] == 'NOT_OK':
    print("Database patching failed")
    if res['data']['database']['patch'].get('database_restore_result') == 'OK':
     print("Restore should be OK - please check schema.db schema file")
    else:
     print("Restore failed too!")
     print("- Restore manually case needed")
     print("- Make sure that configured user has access to database:")
     print("CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';"%(config['database']['username'],config['database']['password']))
     print("GRANT ALL PRIVILEGES ON %s.* TO '%s'@'localhost';"%(config['database']['name'],config['database']['username']))
     print("FLUSH PRIVILEGES;\n\n")
    exit(1)

  db = DB(database,host,username,password)
  db.connect()
  passcode = crypt('changeme', '$1$%s$'%config.get('salt','WBEUAHfO')).split('$')[3]
  res['data']['create_admin_user'] = (db.do("INSERT users (id,name,alias,password) VALUES(1,'Administrator','admin','%s') ON DUPLICATE KEY UPDATE id = id, password = '%s'"%(passcode,passcode)) > 0)
  res['data']['create_master_node'] = (db.do("INSERT nodes (node,url) VALUES('{0}','{1}') ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)".format(config['id'],config['master'])) > 0)
  res['data']['master_node_id']  = db.get_last_id()
  res['data']['create_generic_device'] = (db.do("INSERT device_types (id,name,base) VALUES (0,'generic','generic') ON DUPLICATE KEY UPDATE id = 0") > 0)

  sql ="INSERT device_types (name,base,icon,functions,oid) VALUES ('%(name)s','%(base)s','images/%(icon)s','%(functions)s','%(oid)s') ON DUPLICATE KEY UPDATE oid = %(oid)s, icon = 'images/%(icon)s', functions = '%(functions)s'"
  for type in device_types:
   try:    res['data']['devices_new'] += db.do(sql%type)
   except Exception as err: res['info']['devices'] = str(err)

  sql = "INSERT service_types (service,type) VALUES ('%(service)s','%(type)s') ON DUPLICATE KEY UPDATE id = id"
  for type in service_types:
   try:   res['data']['services_new'] += db.do(sql%type)
   except Exception as err: res['info']['services'] = str(err)

  db.close()

 except Exception as e:
  #from traceback import print_exc
  # print_exc(5)
  print("Error: %s"%str(e))

else:
 try: res['data']['register'] = rest_call("%s/register"%config['master'], aHeader = {'X-Token':config.get('token')}, aArgs = {'id':config['id'],'port':config['port']}, aDataOnly = True)
 except Exception as e: res['info']['register'] = str(e)

res['status'] = 'OK' if len(res['info']) == 0 else 'NOT_OK'
############################################### ALL #################################################
#
# End
#
print(dumps(res,indent=4,sort_keys=True))
exit(0 if res.get('status') == 'OK' else 1)
