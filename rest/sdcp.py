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
 ret = {'title':PC.generic['name'],'portal':"sdcp_portal",'message':"Welcome to the Management Portal",'parameters':[]}
 with DB() as db:
  db.do("SELECT CONCAT(id,'_',name) as id, name FROM users ORDER BY name")
  rows = db.get_rows()
 ret['choices'] = [{'display':'Username', 'id':'sdcp_login', 'data':rows}]
 ret['cookie'] = ",".join(["%s=%s"%(k,v) for k,v in aDict.iteritems()])
 return ret

#
# Clear logs
#
def logs_clear(aDict):
 from ..core.logger import log
 logfiles = aDict.get('logs')
 ret = {}
 for logfile in logfiles:
  try:
   open(logfile,'w').close()
   log("Emptied log [{}]".format(logfile))
   ret[logfile] = 'CLEARED'
  except Exception as err:
   ret[logfile] = 'ERROR:{}'.format(str(err))
 return ret

#
# - count: number of lines
# - logs: list of files to open locally
#
def logs_get(aDict):
 count = int(aDict.get('count',15))
 logfiles = aDict['logs']
 ret = {}
 for logfile in logfiles:
  logs = ["\r" for i in range(count)]
  pos = 0
  try:
   with open(logfile,'r') as f:
    for line in f:
     logs[pos] = line
     pos = (pos + 1) % count
    ret[logfile] = [logs[(pos + n) % count][:-1] for n in reversed(range(count))]
  except Exception as err:
   ret[logfile] = ['ERROR: {}'.format(str(err))]
 return ret
