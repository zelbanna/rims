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

