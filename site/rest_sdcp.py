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

#
# Examine log
#
# - count: number of lines
# - logs: list of files to open locally
#
def examine_logs(aDict):
 count = aDict.get('count',15)
 logfiles = aDict.get('logs',[])
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
