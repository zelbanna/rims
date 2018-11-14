#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Installer"""
__author__ = "Zacharias El Banna"

from sys import argv, stdout, path as syspath
from json import load,dump,dumps
from os import remove, chmod, listdir, path as ospath
from subprocess import check_call
pkgdir = ospath.abspath(ospath.dirname(__file__))
basedir = ospath.abspath(ospath.join(pkgdir,'..'))
syspath.insert(1, basedir)
from rims.core.common import DB, rest_call
res = {}

if len(argv) < 2:
 print("Usage: %s </path/json file>\n"%argv[0])
 print("1) Set up config.json first - see example 'templates/config.json'")
 print("2) Then import database schema.db")
 print("3a) tools/mysql_dumps </path/json file> -r schema.db  (first time install)")
 print("3b) tools/mysql_patch </path/json file> schema.db     (subsequent install)")
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
res['engine']= {'template':config['template'],'install':check_call([engine_run,"install"])}

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
 res['pymysql'] = 'install'
 pipmain(["install", "-q","pymysql"])
try: import dns
except ImportError:
 res['dns'] = 'install'
 pipmain(["install", "-q","dnspython"])
try: import paramiko
except ImportError:
 res['ssh'] = 'install'
 pipmain(["install", "-q","paramiko"])
try: import git
except ImportError:
 res['git'] = 'install'
 pipmain(["install","-q","gitpython"])
try: import pyVmomi
except ImportError:
 res['pyVmomi'] = 'install'
 pipmain(["install","-q","pyVmomi"])
try: import netsnmp
except ImportError:
 res['netsnmp'] = 'install'
 pipmain(["install","-q","python3-netsnmp"])
try: import jnpr.junos
except ImportError:
 res['junos-eznc'] = 'install'
 pipmain(["install","-q","junos-eznc"])

############################################ MASTER ###########################################
#
# Install necessary modules
#
if config['id'] == 'master':
 from importlib import import_module

 try: import eralchemy
 except ImportError:
  res['gitpython'] = 'install'
  pipmain(["install","-q","eralchemy"])

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
 res['device_found'] = len(device_types)
 res['device_new'] = 0

 #
 # Service types
 #
 srvdir = ospath.abspath(ospath.join(pkgdir,'rest'))
 service_types = []
 for file in listdir(srvdir):
  pyfile = file[:-3]
  if file[-3:] == ".py" and pyfile[:2] != "__":
   try:
    mod = import_module("rims.rest.%s"%(pyfile))
    type = getattr(mod,'__type__',None)
    if type:
     service_types.append({'name':pyfile, 'base':type})
   except: pass
 res['service_found'] = len(service_types)
 res['service_new'] = 0


 #
 # Menu items
 #
 sitedir= ospath.abspath(ospath.join(pkgdir,'site'))
 resources = []
 for file in listdir(sitedir):
  pyfile = file[:-3]
  if file[-3:] == ".py" and pyfile[:2] != "__":
   try:
    mod  = import_module("rims.site.%s"%(pyfile))
    type = getattr(mod,'__type__',None)
    icon = getattr(mod,'__icon__',None)
    if type:
     resources.append({'name':pyfile, 'icon':icon, 'type':type})
   except: pass
 res['resources_new'] = 0


 #
 # Common config and user - for master...
 #
 from rims.rest import mysql
 try:
  database,host,username,password = config['db_name'],config['db_host'],config['db_user'],config['db_pass']
  database_args = {'host':host,'username':username,'password':password,'database':database,'schema_file':ospath.join(pkgdir,'schema.db')}
  res['database']= {}
  res['database']['diff'] = mysql.diff(None, database_args)
  if res['database']['diff']['diffs'] > 0:
   res['database']['patch'] = mysql.patch(None, database_args)
   if res['database']['patch']['status'] == 'NOT_OK':
    print("Database patching failed")
    if res['database']['patch'].get('database_restore_result') == 'OK':
     print("Restore should be OK - please check schema.db schema file")
    else:
     print("Restore failed too!")
     print("- Restore manually case needed")
     print("- Make sure that configured user has access to database:")
     print("CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';"%(config['db_user'],config['db_pass']))
     print("GRANT ALL PRIVILEGES ON %s.* TO '%s'@'localhost';"%(config['db_name'],config['db_user']))
     print("FLUSH PRIVILEGES;\n\n")
    exit(1)

  db = DB(database,host,username,password)
  db.connect()

  res['admin_user'] = (db.do("INSERT users (id,name,alias,password) VALUES(1,'Administrator','admin','4cb9c8a8048fd02294477fcb1a41191a') ON DUPLICATE KEY UPDATE id = id, password = '4cb9c8a8048fd02294477fcb1a41191a'") > 0)
  res['node_add'] = (db.do("INSERT nodes (node,url,system) VALUES('{0}','{1}',1) ON DUPLICATE KEY UPDATE system = 1, id = LAST_INSERT_ID(id)".format(config['id'],config['master'])) > 0)
  res['node_id']  = db.get_last_id()
  res['dns_server_add'] = (db.do("INSERT servers (node,service,type) VALUES ('master','nodns','DNS') ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)") > 0)
  res['dns_server_id']  = db.get_last_id()
  res['dns_domain_add'] = (db.do("INSERT domains (id,foreign_id,name,server_id,type ) VALUES (0,0,'local',{},'forward') ON DUPLICATE KEY UPDATE id = 0".format(res['dns_server_id'])) > 0)
  res['generic_device'] = (db.do("INSERT device_types (id,name,base) VALUES (0,'generic','generic') ON DUPLICATE KEY UPDATE id = 0") > 0)

  sql ="INSERT device_types (name,base,icon,functions,oid) VALUES ('%(name)s','%(base)s','../images/%(icon)s','%(functions)s','%(oid)s') ON DUPLICATE KEY UPDATE oid = %(oid)s, icon = '../images/%(icon)s', functions = '%(functions)s'"
  for type in device_types:
   try:    res['device_new'] += db.do(sql%type)
   except Exception as err: res['device_errors'] = str(err)

  sql = "INSERT service_types (name,base) VALUES ('%(name)s','%(base)s') ON DUPLICATE KEY UPDATE id = id"
  for type in service_types:
   try:    res['service_new'] += db.do(sql%type)
   except Exception as err: res['service_errors'] = str(err)

  sql = "INSERT resources (node,title,href,icon,type,user_id,view) VALUES ('%s','{}','{}','../images/{}','{}',1,0) ON DUPLICATE KEY UPDATE id = id"%config['id']
  for item in resources:
   try:    res['resources_new'] += db.do(sql.format(item['name'].title(),"%s_main"%item['name'],item['icon'],item['type']))
   except Exception as err: res['resources_errors'] = str(err)

  db.close()

  #
  # Generate ERD and save
  #
  erd_input = "mysql+pymysql://%s:%s@%s/%s"%(username,password,host,database)
  erd_output= ospath.join(pkgdir,'infra','erd.pdf')
  try:
   from eralchemy import render_er
   render_er(erd_input,erd_output)
   res['ERD'] = 'OK'
  except Exception as e:
   res['ERD'] = str(e)

 except Exception as e:
  #from traceback import print_exc
  # print_exc(5)
  print("Error: %s"%str(e))

else:
 try: res['register'] = rest_call("%s/system/register/%s"%(config['master'],config['id']), aArgs = {'port':config['port'],'system':'1'})['data']
 except Exception as e: res['register'] = str(e)

############################################### ALL #################################################
#
# End
#
print(dumps(res,indent=4,sort_keys=True))
exit(0 if res.get('res') == 'OK' else 1)
