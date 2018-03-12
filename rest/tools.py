"""SDCP tools REST module. Provides various tools"""
__author__ = "Zacharias El Banna"
__version__ = "18.03.07GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from ..core.common import DB,SC

#
#
def settings(aDict):
 with DB() as db:
  db.do("SELECT section,parameter,value,description FROM settings WHERE NOT section = 'system'")
  ret = db.get_rows()
 return ret

#
#
def system(aDict):
 """Function docstring for system TBD

 Args:
  - user_id (required)
 
 Output:
 """
 from resources import list as resource_list
 ret = {}
 with DB() as db:
  db.do("SELECT id,value,parameter FROM settings WHERE section = 'node'")
  ret['nodes'] = [node for node in db.get_rows() if node['parameter'] in SC.system['nodes'].split(',')]
  db.do("SELECT id, icon, title, href, type, inline, user_id FROM resources WHERE type = 'monitor' AND (user_id = %s OR private = 0) ORDER BY type,title"%ret.get('user_id',1))
  ret['monitors'] = db.get_dict(aDict.get('dict')) if aDict.get('dict') else db.get_rows()
 ret['dns_node'] = SC.dns['node']
 ret['dns_type'] = SC.dns['type']
 ret['dhcp_node'] = SC.dhcp['node']
 ret['dhcp_type'] = SC.dhcp['type']
 ret['id'] = SC.system['id']
 return ret

#
#
def install(aDict):
 """Function docstring for install. Installation of SDCP tools and DB entries

 Args:

 Output:
 """
 from os import listdir, path as ospath
 
 packagedir = ospath.abspath(ospath.join(ospath.dirname(__file__),'..'))
 ret = {'res':'NOT_OK'}
 modes = SC.system['mode'].split(',')

 if 'front' in modes:
  from shutil import copy
  # Copy files
  for type,dest in [('images',ospath.join(SC.system['docroot'],'images')), ('infra',SC.system['docroot'])]:
   for file in listdir(ospath.join(packagedir,type)):
    copy(ospath.join(packagedir,type,file), ospath.join(dest,file))
   ret[type] = 'OK'

  # Generate ERD
  try:
   from eralchemy import render_er
   erd_input = "mysql+pymysql://%s:%s@%s/%s"%(SC.database['username'],SC.database['password'],SC.database['host'],SC.database['database'])
   erd_output= ospath.join(SC.system['docroot'],"sdcp.pdf")
   render_er(erd_input,erd_output)
   ret['ERD'] = 'OK'
  except Exception, e:
   ret['error'] = str(e)
   ret['ERD'] = 'NOT_OK'

 #
 # Database stuff
 #
 if 'master' in modes:
  from ..core.mysql import diff
  from importlib import import_module

  # Database diffs
  ret['DB']= diff({'file':ospath.join(packagedir,'mysql.db')})

  # Device types
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
  ret['resources_new'] = 0
  with DB() as db:
   sql ="INSERT INTO resources(title,href,icon,type,user_id,inline) VALUES ('{}','{}','{}','{}',1,1) ON DUPLICATE KEY UPDATE id = id"
   for item in resources:
    try:    ret['resources_new'] += db.do(sql.format(item['name'].title(),"sdcp.cgi?call=%s_main"%item['name'],item['icon'],item['type']))
    except: ret['resources_errors'] = True

 # Done
 ret['res'] = 'OK'
 return ret


#
#
def database(aDict):
 """Function docstring for database TBD

 Args:
  - table (optional)
  - columns (optional) - columns is a string list x,y,z,..

 Output:
 """
 cols = aDict.get('columns','*')
 tbl  = aDict.get('table','devices')
 ret  = {}
 with DB() as db:
  ret['found'] = db.do("SELECT {} FROM {}".format(cols,tbl))
  ret['db'] = db.get_rows() if ret['found'] > 0 else []
 return ret


############################################ REST tools ############################################
#
#
def rest_analyze(aDict):
 """Function docstring for rest_analyze. Analyzes REST files to deduce parameter inputs

 Args:
  - file (required)

 Output:
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


#
#
def rest_explore(aDict):
 """Function docstring for rest_explore TBD

 Args:
  - api (optional)

 Output:
 """
 from types import FunctionType as function
 from importlib import import_module
 def __analyze(aFile):
  data = {'api':aFile, 'functions':[]}
  try:
   module = import_module("sdcp.rest.%s"%(aFile))
   data['functions'] = [item for item in dir(module) if item[0:2] != "__" and isinstance(getattr(module,item,None),function)]
  except Exception,e: data['error'] = str(e)
  return data

 ret = {'data':[]}
 if aDict.get('api'):
  ret['data'].append(__analyze(aDict.get('api')))
 else:
  from os import path as ospath, listdir
  restdir = ospath.abspath(ospath.join(ospath.dirname(__file__)))
  for restfile in listdir(restdir):
   if restfile[-3:] == '.py':
    ret['data'].append(__analyze(restfile[0:-3]))
 return ret

#
#
def rest_information(aDict):
 """Function docstring for rest_explore TBD

 Args:
  - api (required)
  - function (required)

 Output:
 """ 
 from importlib import import_module
 mod = import_module("sdcp.rest.%s"%(aDict['api']))
 fun = getattr(mod,aDict['function'],None)
 return {'api':aDict['api'],'module':mod.__doc__.split('\n'),'information':fun.__doc__.split('\n')}

#
#
def rest_debug(aDict):
 """Function docstring for rest_debug TBD

 Args:

 Output:
 """ 
 print "Set-Cookie: debug=true; Path=/"
 return { 'globals':str(globals().keys()), 'locals':str(locals().keys()) }

############################################ Monitor ##############################################

#
#
def logs_clear(aDict):
 """Function docstring for logs_clear TBD

 Args:

 Output:
 """
 from ..core.logger import log
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

 Output:
 """
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

