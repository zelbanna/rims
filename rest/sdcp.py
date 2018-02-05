"""Module docstring.

SDCP generic REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

from ..core.dbase import DB

#
#
def application(aDict):
 """ Default login information """
 from .. import PackageContainer as PC
 ret = {'portal':"sdcp_portal",'message':"Welcome to the Management Portal",'parameters':[]}
 with DB() as db:
  xist = db.do("SELECT value FROM settings WHERE type = 'generic' AND parameter = 'title'")
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
 ret = {} 
 with DB() as db:
  ret['xist'] = db.do("SELECT parameter,value FROM settings WHERE type = 'logs'")
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
 ret = {}
 with DB() as db:
  ret['xist'] = db.do("SELECT parameter,value FROM settings WHERE type = 'logs'")
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
