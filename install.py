#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Installer"""
__author__ = "Zacharias El Banna"
__version__ = "7.5"

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
parser.add_argument('-c','--config', help = 'Config file',default = 'config.json', required=False)
parser.add_argument('-s','--schema', help = 'Database Schema file',default = 'schema.db', required=False)
parser.add_argument('-t','--startup', help = 'Startup template file',default = 'debian.init', required=False)
# parser.add_argument('-e','--esxi', help = 'Add pyVMOmi',default = None, required=False)
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

############################################### ALL #################################################
#
# Write OS dependent startup file and call 'install' upon it
#
with open(ospath.abspath(ospath.join(pkgdir,'templates',parsedinput.startup)),'r') as f:
 template = f.read()
template = template.replace("%PKGDIR%",pkgdir)
template = template.replace("%CFGFILE%",config_file)
engine_run = ospath.abspath(ospath.join(pkgdir,parsedinput.startup))
with open(engine_run,'w+') as f:
 f.write(template)
chmod(engine_run,0o755)
res['data']['engine']= {'startup':parsedinput.startup,'install':check_call([engine_run,"install"])}

############################################### ALL #################################################
#
# Modules
#
if config.get('database'):
 try:
  import pymysql
 except ImportError as e:
  res['info']['pymysql'] = f'installing ({e})'
  pipmain(["install", "-q","pymysql"])
 else:
  res['modules']['pymysql'] = 'Installed'

if config.get('influxdb'):
 try:
  import influxdb_client
 except ImportError as e:
  res['info']['influxdb'] = f'installing ({e})'
  pipmain(['install','-q','influxdb_client'])
 else:
  res['modules']['influxdb'] = 'Installed'

if config.get('netconf') or config.get('esxi'):
 try:
  import paramiko
 except ImportError as e:
  res['info']['ssh'] = f'installing ({e})'
  pipmain(["install", "-q","paramiko"])
 else:
  res['modules']['ssh'] = 'Installed'

if config.get('esxi'):
 try:
  import pyVmomi
 except ImportError as e:
  res['info']['pyVmomi'] = f'installing ({e})'
  pipmain(["install","-q","pyVmomi"])
 else:
  res['modules']['pyVmomi'] = 'Installed'

if config.get('snmp'):
 try:
  import netsnmp
 except ImportError as e:
  res['info']['netsnmp'] = f'installing ({e})'
  pipmain(["install","-q","python3-netsnmp"])
 else:
  res['modules']['netsnmp'] = 'Installed'

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
   except: pass
   else:
    if tp:
     service_types.append({'service':pyfile, 'type':tp})
 res['data']['services_found'] = len(service_types)
 res['data']['services_new'] = 0

 #
 # Common config and user - for master...
 #
 from rims.api.mysql import diff, patch
 from crypt import crypt
 try:
  settings = config['database']
  database,host,username,password = settings['name'],settings['host'],settings['username'],settings['password']
  database_args = {'host':host, 'username':username, 'password':password, 'database':database, 'schema_file':ospath.join(pkgdir,parsedinput.schema)}
  res['data']['database']= {}
  res['data']['database']['diff'] = diff(None, database_args)
  if res['data']['database']['diff']['diffs'] > 0:
   res['data']['database']['patch'] = patch(None, database_args)
   if res['data']['database']['patch']['status'] == 'NOT_OK':
    print("Database patching failed")
    if res['data']['database']['patch'].get('database_restore_result') == 'OK':
     print("Restore should be OK - please check schema.db schema file")
    else:
     print("Restore failed too!")
     print("- Restore manually case needed")
     print("- Make sure that configured user has access to database:")
     print(f"CREATE USER '{settings['username']}'@'localhost' IDENTIFIED BY '{settings['password']}';")
     print(f"GRANT ALL PRIVILEGES ON {settings['name']}.* TO '{settings['username']}'@'localhost';")
     print("FLUSH PRIVILEGES;\n\n")
    sysexit(1)

  db = DB(database,host,username,password)
  db.connect()
  passcode = crypt('changeme', f"$1${config.get('salt','WBEUAHfO')}$").split('$')[3]
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
