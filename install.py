#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Program docstring.

Installs SDCP

"""
__author__ = "Zacharias El Banna"
__version__ = "18.03.07GA"
__status__ = "Production"

from sys import argv, path as syspath
from json import load,dump,dumps
syspath.insert(1, '../')
if len(argv) < 2:
 print "Usage: {} </path/json file>".format(argv[0])
 print "\n!!! Import DB structure from mysql.db before installing !!!\n"
 exit(0)

from os import remove, chmod, path as ospath
packagedir = ospath.abspath(ospath.dirname(__file__))
basedir = ospath.abspath(ospath.join(packagedir,'..'))

res = {}
#
# load settings
settingsfilename = ospath.abspath(argv[1])
with open(settingsfilename) as settingsfile:
 settings = load(settingsfile)
settings['system']['config_file'] = {'description':'SDCP config file','value':settingsfilename}
modes = settings['system']['mode']['value'].split(',')
res['modes'] = modes

#
# Write Logger
logger = ospath.abspath(ospath.join(packagedir,'core','logger.py'))
try: remove(logger)    
except: pass
with open(logger,'w') as f:
 f.write("def log(aMsg,aID=None):\n")
 f.write(" from time import localtime, strftime\n")
 f.write(" with open('" + settings['logs']['syslog']['value'] + "', 'a') as f:\n")
 f.write(repr("  f.write(unicode('{} ({}): {}\n'.format(strftime('%Y-%m-%d %H:%M:%S', localtime()), aID, aMsg)))")[1:-1] + "\n")

#
# Write CGI files
#
destinations = ['rest']
if 'front' in modes:
 destinations.append('index')
 destinations.append('sdcp')
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

#
# Install necessary modules
#
if 'master' in modes:
 from pip import main as pipmain
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

 # Common settings and user
 try:
  from sdcp.core.common import DB
  with DB() as db:
   res['admin_user'] = db.do("INSERT INTO users(id,name,alias) VALUES(1,'Administrator','admin') ON DUPLICATE KEY UPDATE id = id")
   res['settings'] = 0
   sql = "INSERT INTO settings(section,parameter,value,required,description) VALUES('%s','%s','%s',1,'%s')"
   # db.do("TRUNCATE TABLE settings")
   #
   # When everything is done insert above again
   #
   for section,content in settings.iteritems():
    for k,p in content.iteritems():
     db.do(sql%(section,k,p['value'],p['description']))
     res['settings'] += 1
 except Exception as e:
  res['DB'] = 'NOT_OK'
  res['DB_error'] = str(e)
  print "\nError in settings up database, make sure that configured user has access:\n"
  print "CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';"%(settings['database']['username']['value'],settings['database']['password']['value'])
  print "GRANT ALL PRIVILEGES ON %s.* TO '%s'@'localhost';"%(settings['database']['database']['value'],settings['database']['username']['value'])
  print "FLUSH PRIVILEGES;\n"
else:
 from sdcp.core.rest import call as rest_call
 try:    common_settings = rest_call("%s?tools_settings"%settings['system']['master']['value'],settings['system']['id']['value'])['data']
 except: common_settings = []

#
# Write settings containers
#

for setting in common_settings:
 section = setting.pop('section')
 if not settings.get(section):
  settings[section] = {}
  settings[section][setting['parameter']] = {'description':setting['description'],'value':setting['value']}
try:
 scfile = ospath.abspath(ospath.join(ospath.dirname(__file__),'SettingsContainer.py'))
 with open(scfile,'w') as f:
  for section,content in settings.iteritems():
   processed = {}
   for param,data in content.iteritems():
    processed[param]= data['value'] 
   f.write("%s=%s\n"%(section,dumps(processed)))
  res['containers'] = 'OK'
except Exception,e:
 res['containers'] = 'NOT_OK'
 print str(e)


from sdcp.rest.tools import install
rest = install({})
res.update(rest)

print dumps(res,indent=4,sort_keys=True)
exit(0 if res.get('res') == 'OK' else 1)
