#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Program docstring.

Installs SDCP

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

from sys import argv, path as syspath
from json import load,dumps
syspath.insert(1, '../')
if len(argv) < 2:
 print "Usage: {} </path/json file>".format(argv[0])
 print "\n!!! Please import DB structure from mysql.txt before installing !!!\n"
 exit(0)

from os import chmod, path as ospath
from shutil import copy
res = {}
#
# load settings
settingsfilename = ospath.abspath(argv[1])
with open(settingsfilename) as settingsfile:
 settings = load(settingsfile)
settings['generic']['config_file'] = {'required':'1','description':'SDCP config file','value':settingsfilename}

#
# Verify necessary modules
try: import pymysql
except ImportError:
 res['pymysql'] = 'install'
 pip.main(["install", "-q","pymysql"])
try: import git
except ImportError:
 res['gitpython'] = 'install'
 pip.main(["install","-q","gitpython"])
try: import eralchemy
except ImportError:
 res['gitpython'] = 'install'
 pip.main(["install","-q","eralchemy"])

#
# Write CGI files
basedir = ospath.abspath(ospath.join(ospath.dirname(__file__),'..'))
for dest in [ 'index','rest','sdcp' ]:
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
 for key,values in settings.iteritems():
  file= ospath.abspath(ospath.join(ospath.dirname(__file__),'settings',"%s.py"%key))
  processed = {}
  for param,data in values.iteritems():
   processed[param]= data['value'] 
  with open(file,'w') as f:
    f.write("data=%s"%dumps(processed))    
  res['containers'] = 'OK'
except Exception,e:                   
  res['containers'] = 'NOT_OK'
  print str(e)

from sdcp.rest.sdcp import install
print install({})
print dumps(res,indent=4)
exit(0 if res.get('res') == 'OK' else 1)
