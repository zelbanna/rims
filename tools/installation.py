"""Module docstring.
Install Package content
"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

def install(aDict):
 from sys import path as syspath
 from os import chmod, getcwd, remove, listdir, path as ospath
 from shutil import copy
 import pip
 ret = {'res':'NOT_OK'}
 basedir    = ospath.abspath(ospath.join(ospath.dirname(__file__),'../..'))
 packagedir = ospath.abspath(ospath.join(ospath.dirname(__file__),'..'))
 pcfile  = "{}/PackageContainer.py".format(packagedir)
 logger  = "{}/core/logger.py".format(packagedir)
 syspath.append(basedir)
 #
 # Write Package Container
 try:
  with open(pcfile,'w') as f:
   for name,category in aDict.iteritems():
    f.write("{}={}\n".format(name,repr(category)))
   f.write("repo={}\n".format(repr(packagedir)))
  import sdcp.PackageContainer as PC
  remove(pcfile)
  ret['pc'] = 'OK'
 except Exception as err:
  ret['pc'] = 'NOT_OK'
  ret['error'] = str(err)
  return ret

 #
 # Verify necessary modules
 try: import pymysql
 except ImportError:
  ret['pymysql'] = 'install'
  pip.main(["install", "-q","pymysql"])
 try: import git
 except ImportError:
  ret['gitpython'] = 'install'
  pip.main(["install","-q","gitpython"])
 try: import eralchemy
 except ImportError:
  ret['gitpython'] = 'install'
  pip.main(["install","-q","eralchemy"])

 #
 # Write Logger
 try:
  remove(logger)
 except:
  pass
 with open(logger,'w') as f:
  f.write("def log(aMsg,aID=None):\n")
  f.write(" from time import localtime, strftime\n")
  f.write(" with open('" + PC.generic['logformat'] + "', 'a') as f:\n")
  f.write(repr("  f.write(unicode('{} ({}): {}\n'.format(strftime('%Y-%m-%d %H:%M:%S', localtime()), aID, aMsg)))")[1:-1] + "\n")
 from sdcp.core.logger import log
 log("installation({})".format(aDict))

 #
 # Write CGI files
 for dest in [ 'index','rest', PC.generic['sitebase'] ]:
  site = "{}/{}.cgi".format(PC.generic['docroot'],dest)
  with open(site,'w') as f:
   wr = f.write
   wr("#!/usr/bin/python\n")
   wr("# -*- coding: utf-8 -*-\n")
   wr("from sys import path as syspath\n")
   wr("syspath.insert(1, '{}')\n".format(basedir))
   if dest == 'rest':
    wr("from {0}.core import rest as cgi\n".format(PC.generic['sitebase']))
   else:
    wr("from {0}.core.www import Web\n".format(PC.generic['sitebase']))
    wr("cgi = Web('{}')\n".format(PC.generic['sitebase']))
   wr("cgi.server()\n")
  chmod(site,0755)
  ret["cgi_{}".format(dest)] = 'OK'

 #
 # Generate ERD
 try:
  from eralchemy import render_er
  erd_input = "mysql+pymysql://{}:{}@127.0.0.1/{}".format(PC.generic['dbuser'],PC.generic['dbpass'],PC.generic['db'])
  erd_output= ospath.join(PC.generic['docroot'],PC.generic['sitebase']) + ".pdf"
  render_er(erd_input,erd_output)
  ret['ERD'] = 'OK'
 except Exception, e:
  ret['error'] = str(e)
  ret['ERD'] = 'NOT_OK'
 
 #
 # Copy files
 for type,dest in [('images',ospath.join(PC.generic['docroot'],'images')), ('infra',PC.generic['docroot'])]:
  for file in listdir(ospath.join(packagedir,type)):
   copy(ospath.join(packagedir,type,file), ospath.join(dest,file))
  ret[type] = 'OK'

 #
 # Insert correct types into modules DB
 if PC.generic.get('db'):
  from sdcp.rest.tools import sync_devicetypes 
  ret['new_devicetypes'] = sync_devicetypes(None)['new']
 ret['res'] = 'OK'
 return ret
