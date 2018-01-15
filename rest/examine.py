"""Module docstring.

 SDCP examine REST API module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

#
# Clear logs
#
def clear_logs(aDict):
 from ..core.logger import log
 logfiles = aDict.get('logs')
 result = {'result':'OK'}
 for logfile in logfiles:
  try:
   open(logfile,'w').close()
   log("Emptied log [{}]".format(logfile))
   result[logfile] = 'CLEARED'
  except Exception as err:
   result[logfile] = 'ERROR:{}'.format(str(err))
   result['result'] = 'NOT_OK'
 return result

#
# Examine log
#
# - count: number of lines
# - logs: list of files to open locally
#
def get_logs(aDict):
 count = int(aDict.get('count',15))
 logfiles = aDict['logs']
 ret = {'result':'OK', 'logs':{}}
 for logfile in logfiles:
  logs = ["\r" for i in range(count)]
  pos = 0
  try:
   with open(logfile,'r') as f:
    for line in f:
     logs[pos] = line
     pos = (pos + 1) % count
    ret['logs'][logfile] = [logs[(pos + n) % count][:-1] for n in reversed(range(count))]
  except Exception as err:
   ret['logs'][logfile] = ['ERROR: {}'.format(str(err))]
 return ret
