"""Module docstring.

 SDCP generic REST API module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.6.1GA"
__status__ = "Production"

#import sdcp.PackageContainer as PC
#
#
#
def remove_user(aDict):
 import sdcp.core.GenLib as GL
 db = GL.DB()
 db.connect()
 db.do("DELETE FROM users WHERE id = '{}'".format(aDict['id']))
 res =db.commit()
 return {'res':res}

#
# Clear logs
#
def clear_logs(aDict):
 import sdcp.PackageContainer as PC
 logfiles = aDict.get('logs',"").split(',')
 result = {}
 for logfile in logfiles:
  try:
   open(logfile,'w').close()
   PC.log_msg("Emptied log [{}]".format(logfile))
   result[logfile] = 'ok:cleared'
  except Exception as err:
   result[logfile] = 'error:{}'.format(str(err))
 return result

#
# Examine log
#
# - count: number of lines
# - logs: list of files to open locally
#
def examine_logs(aDict):
 count = int(aDict.get('count',15))
 logfiles = aDict.get('logs',"").split(',')
 result = {}
 for logfile in logfiles:
  logs = ["\r" for i in range(count)]
  pos = 0
  try:
   with open(logfile,'r') as f:
    for line in f:
     logs[pos] = line
     pos = (pos + 1) % count
    result[logfile] = [logs[(pos + n) % count][:-1] for n in reversed(range(count))]
  except Exception as err:
   result[logfile] = str(err)
 return result
