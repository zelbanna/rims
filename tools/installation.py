"""Module docstring.
Install Package content
"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

def install(aDict):
 from sys import path as syspath
 from os import chmod, remove, listdir, path as ospath
 from shutil import copy
 from time import time
 import pip
 basedir    = ospath.abspath(ospath.join(ospath.dirname(__file__),'..','..'))
 ret = {'res':'NOT_OK', 'packagedir':packagedir, 'basedir':basedir}
 syspath.append(basedir)

 #
 # Write Logger
 logger  = ospath.abspath(ospath.join(ospath.dirname(__file__),'..','..','core','logger.py'))
 try:
  remove(logger)
 except:
  pass
 with open(logger,'w') as f:
  f.write("def log(aMsg,aID=None):\n")
  f.write(" from time import localtime, strftime\n")
  f.write(" with open('" + aDict['generic']['logformat'] + "', 'a') as f:\n")
  f.write(repr("  f.write(unicode('{} ({}): {}\n'.format(strftime('%Y-%m-%d %H:%M:%S', localtime()), aID, aMsg)))")[1:-1] + "\n")

 #
 # Copy files
 for type,dest in [('images',ospath.join(aDict['generic']['docroot'],'images')), ('infra',aDict['generic']['docroot'])]:
  for file in listdir(ospath.join(packagedir,type)):
   copy(ospath.join(packagedir,type,file), ospath.join(dest,file))
  ret[type] = 'OK'

 #
 # Generate ERD and Insert correct types into modules DB
 if aDict['generic'].get('db'):
  # Generate ERD
  try:
   from eralchemy import render_er
   erd_input = "mysql+pymysql://{}:{}@127.0.0.1/{}".format(aDict['generic']['dbuser'],aDict['generic']['dbpass'],aDict['generic']['db'])
   erd_output= ospath.join(aDict['generic']['docroot'],"sdcp") + ".pdf"
   render_er(erd_input,erd_output)
   ret['ERD'] = 'OK'
  except Exception, e:
   ret['error'] = str(e)
   ret['ERD'] = 'NOT_OK'

  from ..core.dbase import DB
  from ..core.mysql import diff
  ret['DB']= diff({'file':ospath.join(packagedir,'mysql.db')})
  with DB() as db:
   ret['DB_user'] = db.do("INSERT INTO users(id,name,alias) VALUES(1,'Administrator','admin') ON DUPLICATE KEY UPDATE id = id")

  from ..rest.tools import sync_devicetypes, sync_menuitems
  ret['new_devicetypes'] = sync_devicetypes(None)['new']
  ret['new_menuitems']   = sync_menuitems(None)['new']


 # Done
 ret['res'] = 'OK'
 return ret
