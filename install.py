#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Installer"""
__author__ = "Zacharias El Banna"

from sys import argv, stdout, path as syspath
from json import load,dump,dumps
from os import remove, chmod, listdir, path as ospath
pkgdir = ospath.abspath(ospath.dirname(__file__))
basedir = ospath.abspath(ospath.join(pkgdir,'..'))
syspath.insert(1, basedir)
from zdcp.core.common import DB, rest_call
res = {}

if len(argv) < 2:
 stdout.write("Usage: {} </path/json file>\n\n!!! Import DB structure from schema.db before installing !!!\n\n".format(argv[0]))
 exit(0)
else:
 settings_filename = argv[1]

############################################### ALL #################################################
#
# load settings
#
settings = {}
settings_file = ospath.abspath(settings_filename)
with open(settings_file,'r') as sfile:
 settings = load(sfile)
settings['system']['config_file'] = settings_file

############################################### ALL #################################################
#
# Write engine operations files
#
with open(ospath.abspath(ospath.join(pkgdir,'templates',settings['system']['template'])),'r') as f:
 template = f.read()
template = template.replace("%PKGDIR%",pkgdir)
template = template.replace("%CFGFILE%",settings_file)
with open(ospath.abspath(ospath.join(pkgdir,settings['system']['template'])),'w+') as f:
 f.write(template)
chmod(ospath.abspath(ospath.join(pkgdir,settings['system']['template'])),0o755)
res['engine']= settings['system']['template']

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
if settings['system']['id'] == 'master':
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
    mod = import_module("zdcp.devices.%s"%(pyfile))
    type = getattr(mod,'__type__',None)
    icon = getattr(mod,'__icon__','../images/viz-generic.png')
    oid = getattr(mod,'__oid__',0)
    dev = getattr(mod,'Device',None)
    if type:
     device_types.append({'name':pyfile, 'base':type, 'functions':",".join(dev.get_functions()),'icon':icon,'oid':oid })
   except: pass
 res['device_found'] = len(device_types)
 res['device_new'] = 0

 #
 # Server types
 #
 srvdir = ospath.abspath(ospath.join(pkgdir,'rest'))
 server_types = []
 for file in listdir(srvdir):
  pyfile = file[:-3]
  if file[-3:] == ".py" and pyfile[:2] != "__":
   try:
    mod = import_module("zdcp.rest.%s"%(pyfile))
    type = getattr(mod,'__type__',None)
    if type:
     server_types.append({'name':pyfile, 'base':type})
   except: pass
 res['server_found'] = len(server_types)
 res['server_new'] = 0


 #
 # Menu items
 #
 sitedir= ospath.abspath(ospath.join(pkgdir,'site'))
 resources = []
 for file in listdir(sitedir):
  pyfile = file[:-3]
  if file[-3:] == ".py" and pyfile[:2] != "__":
   try:
    mod  = import_module("zdcp.site.%s"%(pyfile))
    type = getattr(mod,'__type__',None)
    icon = getattr(mod,'__icon__',None)
    if type:
     resources.append({'name':pyfile, 'icon':icon, 'type':type})
   except: pass
 res['resources_new'] = 0


 #
 # Common settings and user - for master...
 #
 from zdcp.rest import mysql
 try:
  database,host,username,password = settings['system']['db_name'],settings['system']['db_host'],settings['system']['db_user'],settings['system']['db_pass']
  database_args = {'host':host,'username':username,'password':password,'database':database,'schema_file':ospath.join(pkgdir,'schema.db')}
  res['database']= {}
  res['database']['diff'] = mysql.diff(database_args,None)
  if res['database']['diff']['diffs'] > 0:
   res['database']['patch'] = mysql.patch(database_args,None)
   if res['database']['patch']['result'] == 'NOT_OK':
    stdout.write("Database patching failed!")
    if res['database']['patch'].get('database_restore_result') == 'OK':
     stdout.write("Restore should be OK - please check schema.db schema file\n")
    else:
     stdout.write("Restore failed too! Restore manually\n")
     exit(1)

  db = DB(database,host,username,password)
  db.connect()

  res['admin_user'] = (db.do("INSERT users (id,name,alias,password) VALUES(1,'Administrator','admin','4cb9c8a8048fd02294477fcb1a41191a') ON DUPLICATE KEY UPDATE id = id, password = '4cb9c8a8048fd02294477fcb1a41191a'") > 0)
  res['node_add'] = (db.do("INSERT nodes (node,url,system) VALUES('{0}','{1}',1) ON DUPLICATE KEY UPDATE system = 1, id = LAST_INSERT_ID(id)".format(settings['system']['id'],settings['system']['master'])) > 0)
  res['node_id']  = db.get_last_id()
  res['dns_server_add'] = (db.do("INSERT servers (node,server,type) VALUES ('master','nodns','DNS') ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)") > 0)
  res['dns_server_id']  = db.get_last_id()
  res['dns_domain_add'] = (db.do("INSERT domains (id,foreign_id,name,server_id,type ) VALUES (0,0,'local',{},'forward') ON DUPLICATE KEY UPDATE id = 0".format(res['dns_server_id'])) > 0)
  res['generic_device'] = (db.do("INSERT device_types (id,name,base) VALUES (0,'generic','generic') ON DUPLICATE KEY UPDATE id = 0") > 0)

  sql ="INSERT device_types (name,base,icon,functions,oid) VALUES ('%(name)s','%(base)s','%(icon)s','%(functions)s','%(oid)s') ON DUPLICATE KEY UPDATE oid = %(oid)s, icon = '%(icon)s', functions = '%(functions)s'"
  for type in device_types:
   try:    res['device_new'] += db.do(sql%type)
   except Exception as err: res['device_errors'] = str(err)

  sql = "INSERT server_types (name,base) VALUES ('%(name)s','%(base)s') ON DUPLICATE KEY UPDATE id = id"
  for type in server_types:
   try:    res['server_new'] += db.do(sql%type)
   except Exception as err: res['server_errors'] = str(err)

  sql = "INSERT resources (node,title,href,icon,type,user_id,view) VALUES ('%s','{}','{}','{}','{}',1,0) ON DUPLICATE KEY UPDATE id = id"%settings['system']['id']
  for item in resources:
   try:    res['resources_new'] += db.do(sql.format(item['name'].title(),"%s_main"%item['name'],item['icon'],item['type']))
   except Exception as err: res['resources_errors'] = str(err)


  db.do("SELECT section,parameter,value FROM settings WHERE node = 'master'")
  data = db.get_rows()
  db.do("SELECT 'nodes' AS section, node AS parameter, url AS value FROM nodes")
  data.extend(db.get_rows())

  for setting in data:
   section = setting.pop('section')
   if not settings.get(section):
    settings[section] = {}
   settings[section][setting['parameter']] = setting['value']

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
  stdout.write("\nError in setting up database, make sure that configured user has access:\n\n")
  stdout.write("CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';\n"%(settings['system']['db_user'],settings['system']['db_pass']))
  stdout.write("GRANT ALL PRIVILEGES ON %s.* TO '%s'@'localhost';\n"%(settings['system']['db_name'],settings['system']['db_user']))
  stdout.write("FLUSH PRIVILEGES;\n\n")
  #from traceback import print_exc
  # print_exc(5)
  stdout.flush()
  raise Exception("DB past error (%s)"%str(e))

else:
 try: res['register'] = rest_call("%s/register"%settings['system']['master'],{'node':settings['system']['id'],'port':settings['system']['port'],'system':'1'})['data']
 except Exception as e: res['register'] = str(e)

############################################### ALL #################################################
#
# End
#
stdout.write(dumps(res,indent=4,sort_keys=True))
stdout.write('\n')
exit(0 if res.get('res') == 'OK' else 1)
