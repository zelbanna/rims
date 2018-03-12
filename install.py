#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Program docstring.

Installs System

"""
__author__ = "Zacharias El Banna"
__version__ = "18.03.07GA"
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
settingsfilename = ospath.abspath(argv[1])
with open(settingsfilename) as settingsfile:
 settings = load(settingsfile)
settings['system']['config_file'] = {'description':'SDCP config file','value':settingsfilename}
modes = settings['system']['mode']['value'].split(',')
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
 f.write(" with open('" + settings['logs']['syslog']['value'] + "', 'a') as f:\n")
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
 for type,dest in [('images',ospath.join(settings['system']['docroot']['value'],'images')), ('infra',settings['system']['docroot']['value'])]:
  for file in listdir(ospath.join(packagedir,type)):
   copy(ospath.join(packagedir,type,file), ospath.join(dest,file))
  res[type] = 'OK'

for dest in destinations:
 site = ospath.abspath(ospath.join(settings['system']['docroot']['value'],"%s.cgi"%dest))
 with open(site,'w') as f:
  wr = f.write
  wr("#!/usr/bin/python\n")
  wr("# -*- coding: utf-8 -*-\n")
  wr("from sys import path as syspath\n")
  wr("syspath.insert(1, '{}')\n".format(basedir))
  if dest == 'rest':
   wr("from sdcp.core.rest import server\n")
   wr("server('%s')\n"%(settings['system']['id']['value']))
  else:
   wr("from sdcp.core.www import Web\n")
   wr("cgi = Web('%s')\n"%settings['system']['master']['value'])
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
  database,host,username,password = settings['system']['db_name']['value'],settings['system']['db_host']['value'],settings['system']['db_user']['value'],settings['system']['db_pass']['value'] 
  db = DB(database,host,username,password)
  db.connect()

  res['admin_user'] = db.do("INSERT INTO users(id,name,alias) VALUES(1,'Administrator','admin') ON DUPLICATE KEY UPDATE id = id")

  sql ="INSERT INTO devicetypes(name,base,functions) VALUES ('{0}','{1}','{2}') ON DUPLICATE KEY UPDATE functions = '{2}'"
  for type in device_types:
   try:    res['device_new'] += db.do(sql.format(type['name'],type['base'],",".join(type['functions'])))
   except Exception as err: res['device_errors'] = str(err)

  sql ="INSERT INTO resources(title,href,icon,type,user_id,inline) VALUES ('{}','{}','{}','{}',1,1) ON DUPLICATE KEY UPDATE id = id"
  for item in resources:
   try:    res['resources_new'] += db.do(sql.format(item['name'].title(),"sdcp.cgi?call=%s_main"%item['name'],item['icon'],item['type']))
   except: res['resources_errors'] = True

  db.close()

  from sdcp.rest.mysql import diff
  res['diff']= diff({'username':username,'password':password,'database':database,'file':ospath.join(packagedir,'mysql.db')})

  #
  # Generate ERD and save
  #
  erd_input = "mysql+pymysql://%s:%s@%s/%s"%(username,password,host,database)
  erd_output= ospath.join(settings['system']['docroot']['value'],"sdcp.pdf")
  try:
   from eralchemy import render_er
   render_er(erd_input,erd_output)
   res['ERD'] = 'OK'
  except Exception, e:
   res['ERD'] = str(e)

 except Exception as e:
  stdout.write("\nError in setting up database, make sure that configured user has access:\n\n")
  stdout.write("CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';\n"%(settings['system']['db_user']['value'],settings['system']['db_pass']['value']))
  stdout.write("GRANT ALL PRIVILEGES ON %s.* TO '%s'@'localhost';\n"%(settings['system']['db_name']['value'],settings['system']['db_user']['value']))
  stdout.write("FLUSH PRIVILEGES;\n\n")
  stdout.flush()
  raise Exception("cannot connect to database (%s)"%str(e))

############################################### ALL #################################################
#
# Fetch and update settings from central repo
#
from sdcp.core.rest import call as rest_call
try: master = rest_call("%s?tools_settings_fetch"%settings['system']['master']['value'],{'node':settings['system']['id']['value']})['data']
except: master = {}
settings.update(master)

#
# Write settings containers
#
scfile = ospath.abspath(ospath.join(ospath.dirname(__file__),'SettingsContainer.py'))
try:
 with open(scfile,'w') as f:
  for section,content in settings.iteritems():
   processed = {}
   for param,data in content.iteritems():
    processed[param]= data['value'] 
   f.write("%s=%s\n"%(section,dumps(processed)))
  res['containers'] = 'OK'
except Exception,e:
 res['containers'] = str(e)

############################################### ALL #################################################
#
# End
#
stdout.write(dumps(res,indent=4,sort_keys=True))
stdout.write('\n')
exit(0 if res.get('res') == 'OK' else 1)
