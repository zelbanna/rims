"""Module docstring.

Generic Device

"""
__author__ = "Zacharias El Banna"
__version__ = "17.10.4"
__status__ = "Production"

class GenericDevice(object):
 
 # set a number of entries:
 # - _ip
 # - _id
 # - _logfile
 
 def __init__(self, aIP, aID = None):
  from sdcp import PackageContainer as PC
  self._id = aID
  self._ip = aIP
  self._logfile = PC.generic['logformat']

 def __str__(self):
  return "IP:{} ID:{} Type:{}".format(self._ip, self._id, self.get_type())

 def __enter__(self):
  return self

 def __exit__(self, *ctx_info):
  pass
 
 def get_type(self):
  return "generic"

 def ping_device(self):
  from os import system
  return system("ping -c 1 -w 1 " + self._ip + " > /dev/null 2>&1") == 0

 def log_msg(self, aMsg, aPrint = False):
  from time import localtime, strftime
  output = unicode("{} : {}".format(strftime('%Y-%m-%d %H:%M:%S', localtime()), aMsg))
  if aPrint:
   print output
  with open(self._logfile, 'a') as f:
   f.write(output + "\n")

 def print_conf(self,argdict):
  print "No config for device"

######################################################################################
#
# Generic SNMP Configuration Class
#
class ConfObject(object):

 def __init__(self):
  self._configitems = {}

 def __str__(self):
  return "ConfObject:{}".format(str(self._configitems))

 def __enter__(self):
  return self

 def __exit__(self, *ctx_info):
  pass

 def load_snmp(self):
  pass

 def get_keys(self, aTargetName = None, aTargetValue = None, aSortKey = None):
  if not aTargetName:
   keys = self._configitems.keys()       
  else:        
   keys = []
   for key, entry in self._configitems.iteritems():
    if entry[aTargetName] == aTargetValue:
     keys.append(key) 
  keys.sort(key = aSortKey)
  return keys         

 def get_entry(self, aKey):
  return self._configitems.get(aKey,None)


