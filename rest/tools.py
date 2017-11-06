"""Module docstring.

Tools REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

#
def installation(aDict):
 from sdcp import PackageContainer as PC
 from sdcp.tools.installation import install
 from json import load
 from os import path as ospath
 file = ospath.join(PC.repo,PC.file)
 with open(file) as settingsfile:
  settings = load(settingsfile)
 settings['file'] = str(PC.file)
 res = install(settings)
 ret = {'res':'OK', 'file':file, 'info':res}
 return ret

#
def sync_devicetypes(aDict):
 from os import listdir, path as ospath
 from importlib import import_module
 from sdcp.core.dbase import DB
 path  = ospath.abspath(ospath.join(ospath.dirname(__file__), '../devices'))
 types = []
 new   = 0
 for file in listdir(path):
  pyfile = file[:-3]
  if file[-3:] == ".py" and pyfile[:2] != "__":
   try:
    module = import_module("sdcp.devices.{}".format(pyfile))
    dev = getattr(module,'Device',None)
    if dev:
     types.append({'name':pyfile, 'base':dev.get_type() })
   except:
    pass
 with DB() as db:
  sql ="INSERT INTO devicetypes(name,base) VALUES ('{}','{}') ON DUPLICATE KEY UPDATE id = id"
  for type in types:
   try:
    type['db'] = db.do(sql.format(type['name'],type['base']))
    new = new + type['db']
   except Exception,e :
    print "DB:{}".format(str(e))

 ret = {'res':'OK', 'types':types, 'found':len(types), 'new':new, 'path':path }
 return ret

#
#
def infra(aDict):
 from sdcp.core.dbase import DB
 ret =  {'res':'OK' }
 with DB() as db:
  ret['typexist'] = db.do("SELECT id, name, base FROM devicetypes") 
  ret['types'] = db.get_rows()
  ret['rackxist'] = db.do("SELECT racks.* FROM racks")
  ret['racks'] = db.get_rows()
  ret['racks'].append({ 'id':'NULL', 'name':'Not used'})
  ret['consolexist'] = db.do("SELECT id, name, INET_NTOA(ip) as ipasc FROM consoles") 
  ret['consoles'] = db.get_rows()
  ret['consoles'].append({ 'id':'NULL', 'name':'No Console', 'ip':2130706433, 'ipasc':'127.0.0.1' })
  ret['pduxist'] = db.do("SELECT pdus.*, INET_NTOA(ip) as ipasc FROM pdus")
  ret['pdus'] = db.get_rows()
  ret['pdus'].append({ 'id':'NULL', 'name':'No PDU', 'ip':'127.0.0.1', 'slots':0, '0_slot_id':0, '0_slot_name':'', '1_slot_id':0, '1_slot_name':'' })
 return ret
