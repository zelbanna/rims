#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Program docstring.

Installs System

"""
__author__ = "Zacharias El Banna"
__version__ = "18.03.14GA"
__status__ = "Production"

from sys import argv, stdout, path as syspath
from json import load,dump,dumps
syspath.insert(1, '../')
if len(argv) < 2:
 stdout.write("Usage: {} </path/json file>\n\n!!! Import DB structure from mysql.db before installing !!!\n\n".format(argv[0]))
 exit(0)

from os import remove, chmod, listdir, path as ospath
packagedir = ospath.abspath(ospath.dirname(__file__))
basedir = ospath.abspath(ospath.join(packagedir,'..'))
res = {}

############################################### ALL #################################################
#
# load settings
#
settings = {}
settingsfilename = ospath.abspath(argv[1])
with open(settingsfilename) as sfile:
 temp = load(sfile)
for section,content in temp.iteritems():
 for key,params in content.iteritems():
  if not settings.get(section):
   settings[section] = {}
  settings[section][key] = params['value'] 
settings['system']['config_file'] = settingsfilename
modes = settings['system']['mode'].split(',')
res['modes'] = modes

############################################### ALL #################################################
#
# Write Logger
#
logger = ospath.abspath(ospath.join(packagedir,'core','logger.py'))
try: remove(logger)    
except: pass
with open(logger,'w') as f:
 f.write("def log(aMsg,aID=None):\n")
 f.write(" from time import localtime, strftime\n")
 f.write(" with open('" + settings['logs']['syslog'] + "', 'a') as f:\n")
 f.write(repr("  f.write(unicode('{} ({}): {}\n'.format(strftime('%Y-%m-%d %H:%M:%S', localtime()), aID, aMsg)))")[1:-1] + "\n")

############################################### ALL #################################################
#
# Write CGI files
#
destinations = []

if 'rest' in modes:
 destinations.append('rest')

if 'front' in modes:
 from shutil import copy
 destinations.append('index')
 destinations.append('sdcp')
 # Copy files
 for type,dest in [('images',ospath.join(settings['system']['docroot'],'images')), ('infra',settings['system']['docroot'])]:
  for file in listdir(ospath.join(packagedir,type)):
   copy(ospath.join(packagedir,type,file), ospath.join(dest,file))
  res[type] = 'OK'

for dest in destinations:
 site = ospath.abspath(ospath.join(settings['system']['docroot'],"%s.cgi"%dest))
 with open(site,'w') as f:
  wr = f.write
  wr("#!/usr/bin/python\n")
  wr("# -*- coding: utf-8 -*-\n")
  wr("from sys import path as syspath\n")
  wr("syspath.insert(1, '{}')\n".format(basedir))
  if dest == 'rest':
   wr("from sdcp.core.rest import server\n")
   wr("server('%s')\n"%(settings['system']['id']))
  else:
   wr("from sdcp.core.www import Web\n")
   wr("cgi = Web('%s','%s')\n"%(settings['system']['rest'], settings['system']['id']))
   wr("cgi.server()\n")
 chmod(site,0755)
 res["cgi_{}".format(dest)] = 'OK'

############################################ MASTER ###########################################
#
# Install necessary modules
#
if 'master' in modes:
 from importlib import import_module
 from pip import main as pipmain

 #
 # Modules
 #
 try: import pymysql
 except ImportError:
  res['pymysql'] = 'install'
  pipmain(["install", "-q","pymysql"])
 try: import git
 except ImportError:
  res['gitpython'] = 'install'
  pipmain(["install","-q","gitpython"])
 if 'front' in modes:
  try: import eralchemy
  except ImportError:
   res['gitpython'] = 'install'
   pipmain(["install","-q","eralchemy"])

 #
 # Device types
 #
 devdir = ospath.abspath(ospath.join(packagedir,'devices'))
 device_types = []
 for file in listdir(devdir):
  pyfile = file[:-3]
  if file[-3:] == ".py" and pyfile[:2] != "__":
   try:
    mod = import_module("sdcp.devices.{}".format(pyfile))
    type = getattr(mod,'__type__',None)
    dev = getattr(mod,'Device',None)
    if type:
     device_types.append({'name':pyfile, 'base':type, 'functions':dev.get_functions() })
   except: pass
 res['device_found'] = len(device_types)
 res['device_new'] = 0
 
 #
 # Menu items
 #
 sitedir= ospath.abspath(ospath.join(packagedir,'site'))
 resources = []
 for file in listdir(sitedir):
  pyfile = file[:-3]
  if file[-3:] == ".py" and pyfile[:2] != "__":
   try:
    mod  = import_module("sdcp.site.%s"%(pyfile))
    type = getattr(mod,'__type__',None)
    icon = getattr(mod,'__icon__',None)
    if type:
     resources.append({'name':pyfile, 'icon':icon, 'type':type})
   except: pass
 res['resources_new'] = 0

 #
 # Common settings and user
 #
 from sdcp.core.common import DB
 try:
  database,host,username,password = settings['system']['db_name'],settings['system']['db_host'],settings['system']['db_user'],settings['system']['db_pass'] 
  db = DB(database,host,username,password)
  db.connect()

  res['admin_user'] = db.do("INSERT INTO users(id,name,alias) VALUES(1,'Administrator','admin') ON DUPLICATE KEY UPDATE id = id")
  res['register'] = db.do("INSERT INTO nodes(node,url,system) VALUES('%s','%s',1) ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)"%(settings['system']['id'],settings['system']['rest']))
  res['node_id']= db.get_last_id()
  sql ="INSERT INTO devicetypes(name,base,functions) VALUES ('{0}','{1}','{2}') ON DUPLICATE KEY UPDATE functions = '{2}'"
  for type in device_types:
   try:    res['device_new'] += db.do(sql.format(type['name'],type['base'],",".join(type['functions'])))
   except Exception as err: res['device_errors'] = str(err)

  sql ="INSERT INTO resources(title,href,icon,type,user_id,inline) VALUES ('{}','{}','{}','{}',1,1) ON DUPLICATE KEY UPDATE id = id"
  for item in resources:
   try:    res['resources_new'] += db.do(sql.format(item['name'].title(),"sdcp.cgi?call=%s_main"%item['name'],item['icon'],item['type']))
   except: res['resources_errors'] = True

  db.do("SELECT section,parameter,value FROM settings WHERE node = 'master'")
  data = db.get_rows()
  db.do("SELECT 'node' AS section, node AS parameter, url AS value FROM nodes") 
  data.extend(db.get_rows())

  for setting in data:
   section = setting.pop('section')
   if not settings.get(section):
    settings[section] = {} 
   settings[section][setting['parameter']] = setting['value']

  db.close()

  from sdcp.rest.mysql import diff
  res['diff']= diff({'username':username,'password':password,'database':database,'file':ospath.join(packagedir,'mysql.db')})

  #
  # Generate ERD and save
  #
  erd_input = "mysql+pymysql://%s:%s@%s/%s"%(username,password,host,database)
  erd_output= ospath.join(settings['system']['docroot'],"sdcp.pdf")
  try:
   from eralchemy import render_er
   render_er(erd_input,erd_output)
   res['ERD'] = 'OK'
  except Exception, e:
   res['ERD'] = str(e)

 except Exception as e:
  stdout.write("\nError in setting up database, make sure that configured user has access:\n\n")
  stdout.write("CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';\n"%(settings['system']['db_user'],settings['system']['db_pass']))
  stdout.write("GRANT ALL PRIVILEGES ON %s.* TO '%s'@'localhost';\n"%(settings['system']['db_name'],settings['system']['db_user']))
  stdout.write("FLUSH PRIVILEGES;\n\n")
  stdout.flush()
  raise Exception("cannot connect to database (%s)"%str(e))

elif 'rest' in modes:
 ########################################## NON-MASTER REST ########################################
 #
 # Fetch and update settings from central repo
 #
 from sdcp.core.common import rest_call
 try: res['register'] = rest_call("%s?system_register"%settings['system']['master'],{'node':settings['system']['id'],'url':settings['system']['rest'],'system':'1'})['data']
 except Exception,e: res['register'] = str(e)
 try: master   = rest_call("%s?system_settings_fetch"%settings['system']['master'],{'node':settings['system']['id']})['data']
 except: pass
 else:
  for section,content in master.iteritems():
   if settings.get(section): settings[section].update(content)
   else: settings[section] = content


#
# Write settings containers
#
container = ospath.abspath(ospath.join(ospath.dirname(__file__),'SettingsContainer.py'))
try:
 with open(container,'w') as f:
  f.write("SC=%s\n"%dumps(settings))
  res['container'] = 'OK'
except Exception,e:
 res['container'] = str(e)

############################################### ALL #################################################
#
# End
#
stdout.write(dumps(res,indent=4,sort_keys=True))
stdout.write('\n')
exit(0 if res.get('res') == 'OK' else 1)
