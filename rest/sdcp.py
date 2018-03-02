"""Module docstring.

SDCP generic REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__ = "Production"

def application(aDict):
 """Function docstring for application TBD

 Args:

 Extra:
 """
 from ..core.dbase import DB
 from datetime import datetime,timedelta
 """ Default login information """
 ret = {'message':"Welcome to the Management Portal",'parameters':[]}
 with DB() as db:
  xist = db.do("SELECT value FROM settings WHERE section = 'generic' AND parameter = 'title'")
  ret['title'] = db.get_val('value') if xist > 0 else 'New Installation'
  db.do("SELECT CONCAT(id,'_',name) as id, name FROM users ORDER BY name")
  rows = db.get_rows()
 ret['choices'] = [{'display':'Username', 'id':'sdcp_login', 'data':rows}]
 cookie = aDict
 ret['cookie'] = ",".join(["%s=%s"%(k,v) for k,v in cookie.iteritems()])
 ret['expires'] = (datetime.utcnow() + timedelta(days=1)).strftime("%a, %d %b %Y %H:%M:%S GMT")
 return ret


#
#
def authenticate(aDict):
 from datetime import datetime,timedelta
 ret = {}
 ret['authenticated'] = 'OK'
 ret['expires'] = (datetime.utcnow() + timedelta(days=1)).strftime("%a, %d %b %Y %H:%M:%S GMT")
 return ret

#
#
def logs_clear(aDict):
 """Function docstring for logs_clear TBD

 Args:

 Extra:
 """
 from ..core.logger import log
 from ..core.dbase import DB
 ret = {}
 with DB() as db:
  ret['xist'] = db.do("SELECT parameter,value FROM settings WHERE section = 'logs'")
  logs = db.get_rows()
 for entry in logs:
  try:
   open(entry['value'],'w').close()
   ret[entry['parameter']] = 'CLEARED'
   log("Emptied log [{}]".format(entry['value']))
  except Exception as err:
   ret[entry['parameter']] = 'ERROR: %s'%(str(err))
 return ret

#
#
def logs_get(aDict):
 """Function docstring for logs_get TBD

 Args:
  - count (optional)

 Extra:
 """
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
#
def db_table(aDict):
 """Function docstring for db_table TBD

 Args:
  - table (optional)
  - columns (optional) - columns is a string list x,y,z,..

 Extra:
 """
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
def db_dump(aDict):
 """Function docstring for db_dump TBD

 Args:
  - mode (optional)

 Extra:
 """
 from ..core.mysql import dump
 return dump({'mode':aDict.get('mode','structure')})

#
#
def mac_sync(aDict):
 """Function docstring for mac_sync TBD

 Args:

 Extra:
 """
 from ..core.dbase import DB
 def GL_mac2int(aMAC):  
  try:    return int(aMAC.replace(":",""),16)
  except: return 0
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
    row['xist'] = arps.get(row['ipasc'])
    if row['xist']:
     ret.append(row)
     db.do("UPDATE devices SET mac = {} WHERE id = {}".format(GL_mac2int(row['xist']),row['id']))
 except:
  pass
 return ret

#
#
def install(aDict):
 """Function docstring for install. Installation of SDCP tools and DB entries

 Args:

 Extra:
 """
 from sys import path as syspath
 from os import chmod, remove, listdir, path as ospath
 from importlib import import_module
 from shutil import copy
 from time import time
 import pip
 from ..core.dbase import DB
 from ..core.mysql import diff
 from .. import SettingsContainer as SC

 packagedir = ospath.abspath(ospath.join(ospath.dirname(__file__),'..'))
 devdir = ospath.abspath(ospath.join(packagedir,'devices'))
 sitedir= ospath.abspath(ospath.join(packagedir,'site'))
 logger = ospath.abspath(ospath.join(packagedir,'core','logger.py'))
 ret = {'res':'NOT_OK'}

 modes = SC.generic['mode'].split(',')

 #
 # Write Logger
 try:
  remove(logger)
 except:
  pass
 with open(logger,'w') as f:
  f.write("def log(aMsg,aID=None):\n")
  f.write(" from time import localtime, strftime\n")
  f.write(" with open('" + SC.logs['syslog'] + "', 'a') as f:\n")
  f.write(repr("  f.write(unicode('{} ({}): {}\n'.format(strftime('%Y-%m-%d %H:%M:%S', localtime()), aID, aMsg)))")[1:-1] + "\n")

 if 'front' in modes:
  # Copy files
  for type,dest in [('images',ospath.join(SC.generic['docroot'],'images')), ('infra',SC.generic['docroot'])]:
   for file in listdir(ospath.join(packagedir,type)):
    copy(ospath.join(packagedir,type,file), ospath.join(dest,file))
   ret[type] = 'OK'

  # Generate ERD
  try:
   from eralchemy import render_er
   erd_input = "mysql+pymysql://%s:%s@%s/%s"%(SC.database['username'],SC.database['password'],SC.database['host'],SC.database['database'])
   erd_output= ospath.join(SC.generic['docroot'],"sdcp.pdf")
   render_er(erd_input,erd_output)
   ret['ERD'] = 'OK'
  except Exception, e:
   ret['error'] = str(e)
   ret['ERD'] = 'NOT_OK'

 # Database diffs
 ret['DB']= diff({'file':ospath.join(packagedir,'mysql.db')})
 with DB() as db:
  # Insert required settings, if they do not exist (!) ZEB: Todo
  ret['DB']['settings'] = 0

 # Device types
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
 ret['device_found'] = len(device_types)
 #ret['device_types'] = [tp['name'] for tp in device_types]
 # ret['device_types'].sort()
 ret['device_new'] = 0
 with DB() as db:
  sql ="INSERT INTO devicetypes(name,base,functions) VALUES ('{0}','{1}','{2}') ON DUPLICATE KEY UPDATE functions = '{2}'"
  for type in device_types:
   try:    ret['device_new'] += db.do(sql.format(type['name'],type['base'],",".join(type['functions'])))
   except Exception as err: ret['device_type_errors'] = str(err)

 # Menu items
 menuitems = []
 for file in listdir(sitedir):
  pyfile = file[:-3]
  if file[-3:] == ".py" and pyfile[:2] != "__":
   try:
    mod  = import_module("sdcp.site.%s"%(pyfile))
    icon = getattr(mod,'__icon__',None)
    if icon:
     items.append({'name':pyfile, 'icon':icon})
   except: pass
 ret['menuitems_new'] = 0
 with DB() as db:
  sql ="INSERT INTO resources(title,href,icon,type,user_id,inline) VALUES ('{}','{}','{}','menuitem',1,1) ON DUPLICATE KEY UPDATE id = id"
  for item in menuitems:
   try:    ret['menuitems_new'] += db.do(sql.format(item['name'].title(),"sdcp.cgi?call=%s_main"%item['name'],item['icon']))
   except: ret['menuitems_errors'] = True

 # Done
 ret['res'] = 'OK'
 return ret

#
#
def rest_analyze(aDict):
 """Function docstring for rest_analyze. Analyzes REST files to deduce parameter inputs

 Args:
  - file (required)

 Extra:
 """
 from os import path as ospath
 restdir = ospath.abspath(ospath.join(ospath.dirname(__file__), '..','rest'))
 ret = {'file':aDict['file'],'functions':[],'global':[]}
 data = {'function':None,'required':{},'optional':{},'pop':{},'undecoded':[],'arg':None,'imports':[]}

 with open(ospath.abspath(ospath.join(restdir,aDict['file'])),'r') as file:
  line_no = 0
  for line in file:
   line_no += 1
   line = line.rstrip()
   line = line.replace("%s","<var>")
   if line[0:4] =='from':
    ret['global'].append(line)
   if line[0:4] == 'def ':
    if data['function']:
     ret['functions'].append(data)
     data = {'function':None,'required':{},'optional':{},'pop':{},'undecoded':[],'arg':None,'imports':[]}
    name_end = line.index('(')
    data['arg'] = line[name_end+1:-2]
    data['function'] = line[4:name_end].lstrip()
   elif data['function'] and data['arg'] in line:
    try:
     parts = line.split(data['arg'])
     for part in parts[1:]:
      if part[0:2] == "['":
       end = part.index("]")
       argument = part[2:end-1]
       if not data['required'].get(argument):
        data['required'][argument] = (data['optional'].get(argument) is None)
      elif part[0:6] == ".get('":
       end = part[6:].index("'")
       argument = part[6:6+end]
       if not data['optional'].get(argument):
        data['optional'][argument] = (data['required'].get(argument) is None)
      elif part[0:6] == ".pop('":
       end = part[6:].index("'")
       argument = part[6:6+end]
       if not data['required'].get(argument) and not data['optional'].get(argument):
        data['pop'][argument] = True
      elif part[0:7]== ".keys()" or part[0] == ")" or part[0:12] == ".iteritems()":
       pass
      else:
       data['undecoded'].append({'part':part,'line':line_no})
    except Exception, e:
     data['undecoded'].append({'error':str(e),'line':line_no})
   elif data['function'] and "from" in line:
    data['imports'].append(line.lstrip())
  if data['function']:
   ret['functions'].append(data)
 return ret
