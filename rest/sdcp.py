"""Module docstring.

SDCP generic REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

#
#
def application(aDict):
 from ..core.dbase import DB
 """ Default login information """
 ret = {'portal':"sdcp_portal",'message':"Welcome to the Management Portal",'parameters':[]}
 with DB() as db:
  xist = db.do("SELECT value FROM settings WHERE section = 'generic' AND parameter = 'title'")
  ret['title'] = db.get_val('value') if xist > 0 else 'New Installation'
  db.do("SELECT CONCAT(id,'_',name) as id, name FROM users ORDER BY name")
  rows = db.get_rows()
 ret['choices'] = [{'display':'Username', 'id':'sdcp_login', 'data':rows}]
 ret['cookie'] = ",".join(["%s=%s"%(k,v) for k,v in aDict.iteritems()])
 return ret

#
# Clear logs
#
def logs_clear(aDict):
 from ..core.logger import log as logging
 from ..core.dbase import DB
 ret = {} 
 with DB() as db:
  ret['xist'] = db.do("SELECT parameter,value FROM settings WHERE section = 'logs'")
  logs = db.get_rows()
 for log in logs:
  try:
   open(log['value'],'w').close()
   logging("Emptied log [{}]".format(log['value']))
   ret[log['parameter']] = 'CLEARED'
  except Exception as err:
   ret[log['parameter']] = 'ERROR: %s'%(str(err))
 return ret

#
# - count: number of lines
#
def logs_get(aDict):
 from ..core.dbase import DB
 ret = {}
 with DB() as db:
  ret['xist'] = db.do("SELECT parameter,value FROM settings WHERE section = 'logs'")
  logs = db.get_rows()
 count = int(aDict.get('count',15))
 for log in logs:
  lines = ["\r" for i in range(count)]
  pos = 0
  try:
   with open(log['value'],'r') as f:
    for line in f:
     lines[pos] = line
     pos = (pos + 1) % count
    ret[log['parameter']] = [lines[(pos + n) % count][:-1] for n in reversed(range(count))]
  except Exception as err:
   ret[log['parameter']] = ['ERROR: %s'%(str(err))]
 return ret

#
def sync_devicetypes(aDict):
 from os import listdir, path as ospath
 from importlib import import_module
 from ..core.dbase import DB
 path  = ospath.abspath(ospath.join(ospath.dirname(__file__), '..','devices'))
 types = []
 new   = 0
 for file in listdir(path):
  pyfile = file[:-3]
  if file[-3:] == ".py" and pyfile[:2] != "__":
   try:
    mod = import_module("sdcp.devices.{}".format(pyfile))
    type = getattr(mod,'__type__',None)
    if type:
     types.append({'name':pyfile, 'base':type })
   except:
    pass
 with DB() as db:
  sql ="INSERT INTO devicetypes(name,base) VALUES ('{}','{}') ON DUPLICATE KEY UPDATE id = id"
  for type in types:
   try:
    type['db'] = db.do(sql.format(type['name'],type['base']))
    new += type['db']
   except Exception,e :
    print "DB:{}".format(str(e))

 return {'types':types, 'found':len(types), 'new':new, 'path':path }

#
def sync_menuitems(aDict):
 from os import listdir, path as ospath
 from importlib import import_module
 from ..core.dbase import DB
 path  = ospath.abspath(ospath.join(ospath.dirname(__file__), '..','site'))
 items = []
 for file in listdir(path):
  pyfile = file[:-3]
  if file[-3:] == ".py" and pyfile[:2] != "__":
   try:
    mod  = import_module("sdcp.site.{}".format(pyfile))
    icon = getattr(mod,'__icon__',None)
    if not icon: continue
    else:  items.append({'name':pyfile, 'icon':icon})
   except: pass
 new   = 0
 with DB() as db:
  sql ="INSERT INTO resources(title,href,icon,type,user_id,inline) VALUES ('{}','{}','{}','menuitem',1,1) ON DUPLICATE KEY UPDATE id = id"
  for item in items:
   try:
    item['db'] = db.do(sql.format(item['name'].title(),"sdcp.cgi?call=%s_main"%item['name'],item['icon']))
    new += item['db']
   except: pass
 return {'menuitems':items, 'found':len(items), 'new':new, 'path':path }

#
# db_table(columns)
# - columns is a string list x,y,z,..
#
def db_table(aDict):
 from ..core.dbase import DB
 cols = aDict.get('columns','*')
 tbl  = aDict.get('table','devices')
 ret  = {}
 with DB() as db:
  ret['found'] = db.do("SELECT {} FROM {}".format(cols,tbl))
  ret['db'] = db.get_rows() if ret['found'] > 0 else []
 return ret

#
#
#
def db_dump(aDict):
 from ..core.mysql import dump
 return dump({'mode':aDict.get('mode','structure')})

#
# Linux oriented mac sync
#
def mac_sync(aDict):
 from ..core.genlib import mac2int
 from ..core.dbase import DB
 ret = []
 try:
  arps = {}
  with open('/proc/net/arp') as f:
   _ = f.readline()
   for data in f:
    ( ip, _, _, mac, _, _ ) = data.split()
    if not mac == '00:00:00:00:00:00':
     arps[ip] = mac
  with DB() as db:
   db.do("SELECT id, hostname, INET_NTOA(ip) as ipasc, mac FROM devices WHERE hostname <> 'unknown' ORDER BY ip")
   rows = db.get_rows()
   for row in rows:
    row['xist'] = arps.get(row['ipasc'],None)
    if row['xist']:        
     ret.append(row)
     db.do("UPDATE devices SET mac = {} WHERE id = {}".format(mac2int(row['xist']),row['id']))
 except:
  pass
 return ret


#
#
def install(aDict):
 from sys import path as syspath
 from os import chmod, remove, listdir, path as ospath
 from shutil import copy
 from time import time
 import pip
 from ..core.dbase import DB
 from ..core.mysql import diff
 from ..settings import generic,database,logs
 packagedir = ospath.abspath(ospath.join(ospath.dirname(__file__),'..'))
 logger  = ospath.abspath(ospath.join(packagedir,'core','logger.py'))
 ret = {'res':'NOT_OK'}

 modes = generic.data['mode'].split(',')

 #
 # Write Logger
 try:
  remove(logger)
 except:
  pass
 with open(logger,'w') as f:
  f.write("def log(aMsg,aID=None):\n")
  f.write(" from time import localtime, strftime\n")
  f.write(" with open('" + logs.data['syslog'] + "', 'a') as f:\n")
  f.write(repr("  f.write(unicode('{} ({}): {}\n'.format(strftime('%Y-%m-%d %H:%M:%S', localtime()), aID, aMsg)))")[1:-1] + "\n")

 if 'front' in modes:
  # Copy files
  for type,dest in [('images',ospath.join(generic.data['docroot'],'images')), ('infra',generic.data['docroot'])]:
   for file in listdir(ospath.join(packagedir,type)):
    copy(ospath.join(packagedir,type,file), ospath.join(dest,file))
   ret[type] = 'OK'

  # Generate ERD
  try:
   from eralchemy import render_er
   erd_input = "mysql+pymysql://%s:%s@%s/%s"%(database.data['username'],database.data['password'],database.data['host'],database.data['database'])
   erd_output= ospath.join(generic.data['docroot'],"sdcp.pdf")
   render_er(erd_input,erd_output)
   ret['ERD'] = 'OK'
  except Exception, e:
   ret['error'] = str(e)
   ret['ERD'] = 'NOT_OK'

 ret['DB']= diff({'file':ospath.join(packagedir,'mysql.db')})
 with DB() as db:
  # Insert required user
  ret['DB']['user'] = db.do("INSERT INTO users(id,name,alias) VALUES(1,'Administrator','admin') ON DUPLICATE KEY UPDATE id = id")
  # Insert required settings
  ret['DB']['settings'] = 0

 ret['new_devicetypes'] = sync_devicetypes(None)['new']
 ret['new_menuitems']   = sync_menuitems(None)['new']

 # Done
 ret['res'] = 'OK'
 return ret
