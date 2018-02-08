#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Program docstring.

Installs SDCP

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

from sys import argv, path as syspath
from json import load,dump,dumps
syspath.insert(1, '../')
if len(argv) < 2:
 print "Usage: {} </path/json file>".format(argv[0])
 print "\n!!! Import DB structure from mysql.db before installing !!!\n"
 exit(0)

from os import chmod, path as ospath
from shutil import copy
from pip import main as pipmain
res = {}
#
# load settings
settingsfilename = ospath.abspath(argv[1])
with open(settingsfilename) as settingsfile:
 settings = load(settingsfile)
settings['generic']['config_file'] = {'required':'1','description':'SDCP config file','value':settingsfilename}
modes = settings['generic']['mode']['value'].split(',')
res['modes'] = modes

#
# Verify necessary modules
try: import pymysql
except ImportError:
 res['pymysql'] = 'install'
 pipmain(["install", "-q","pymysql"])
try: import git
except ImportError:
 res['gitpython'] = 'install'
 pipmain(["install","-q","gitpython"])
try: import eralchemy
except ImportError:
 res['gitpython'] = 'install'
 pipmain(["install","-q","eralchemy"])

#
# Write CGI files
basedir = ospath.abspath(ospath.join(ospath.dirname(__file__),'..'))
destinations = ['rest']
if 'front' in modes:
 destinations.append('index')
 destinations.append('sdcp')
for dest in destinations:
 site = ospath.abspath(ospath.join(settings['generic']['docroot']['value'],"%s.cgi"%dest))
 with open(site,'w') as f:
  wr = f.write
  wr("#!/usr/bin/python\n")
  wr("# -*- coding: utf-8 -*-\n")
  wr("from sys import path as syspath\n")
  wr("syspath.insert(1, '{}')\n".format(basedir))
  if dest == 'rest':
   wr("from sdcp.core import rest as cgi\n")
  else:
   wr("from sdcp.core.www import Web\n")
   wr("cgi = Web('%s')\n"%settings['node']['sdcp']['value'])
  wr("cgi.server()\n")
 chmod(site,0755)
 res["cgi_{}".format(dest)] = 'OK'

#
# Write settings containers
try:              
 scfile= ospath.abspath(ospath.join(ospath.dirname(__file__),'SettingsContainer.py'))
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

#
# Update database
#
try:
 from sdcp.core.dbase import DB
 with DB() as db:
  res['admin_user'] = db.do("INSERT INTO users(id,name,alias) VALUES(1,'Administrator','admin') ON DUPLICATE KEY UPDATE id = id")
  res['settings'] = 0
  sql = "INSERT INTO settings(section,parameter,value,required,description) VALUES('%s','%s','%s','%s','%s')"
  db.do("TRUNCATE TABLE settings")
  for section,content in settings.iteritems():
   for key,p in content.iteritems():
    db.do(sql%(section,key,p['value'],p['required'],p['description']))
    res['settings'] += 1
except Exception as e:
 res['DB'] = 'NOT_OK'
 res['DB_error'] = str(e)
 print "\nError in settings up database, make sure that configured user has access:\n"
 print "CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';"%(settings['database']['username']['value'],settings['database']['password']['value'])
 print "GRANT ALL PRIVILEGES ON %s.* TO '%s'@'localhost';"%(settings['database']['database']['value'],settings['database']['username']['value'])
 print "FLUSH PRIVILEGES;\n"
else:
 from sdcp.rest.sdcp import install
 rest = install({})
 res.update(rest)

print dumps(res,indent=4,sort_keys=True)
exit(0 if res.get('res') == 'OK' else 1)
