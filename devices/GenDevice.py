"""Module docstring.

Generic Device

"""
__author__ = "Zacharias El Banna"
__version__ = "17.10.4"
__status__ = "Production"

class GenDevice(object):
 
 # set a number of entries:
 # - _ip
 # - _id
 # - _logfile
 
 def __init__(self, aIP, aID = None, atype = "unknown"):
  import sdcp.PackageContainer as PC
  self._type = atype
  self._id = aID
  self._ip = aIP
  self._logfile = PC.generic['logformat']

 def __str__(self):
  return "IP:{} ID:{} Type:{}".format(self._ip, self._id, self._type)
 
 def ping_device(self):
  from os import system
  return system("ping -c 1 -w 1 " + self._ip + " > /dev/null 2>&1") == 0

 def get_type(self):
  return self._type

 def log_msg(self, aMsg, aPrint = False):
  from time import localtime, strftime
  output = unicode("{} : {}".format(strftime('%Y-%m-%d %H:%M:%S', localtime()), aMsg))
  if aPrint:
   print output
  with open(self._logfile, 'a') as f:
   f.write(output + "\n")

 def print_conf(self,argdict):
  print "No config for device"
