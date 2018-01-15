"""Module docstring.

Generic Device

"""
__author__  = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__  = "Production"
__type__    = "generic"

class Device(object):

 # set a number of entries available for all subclasses:
 # - _ip
 # - _id

 def __init__(self, aIP, aID = None):
  self._id = aID
  self._ip = aIP

 def __str__(self):
  return "IP:%s ID:%s"%(self._ip, self._id)

 def __enter__(self):
  return self

 def __exit__(self, *ctx_info):
  pass

 #
 def threading(self, aOperation, aArgs = None):
  try:
   from threading import Thread
   op = getattr(self, aOperation, None)
   thread = Thread(target = op, args=aArgs)
   thread.name = aOperation
   thread.start()
   self.log_msg("threading started: {}({})".format(aOperation,aArgs))
  except:
   self.log_msg("threading error: Illegal operation passed ({})".format(aOperation))
   thread = None
  return thread

 def ping_device(self):
  from os import system
  return system("ping -c 1 -w 1 " + self._ip + " > /dev/null 2>&1") == 0

 def log_msg(self, aMsg):
  from ..core.logger import log
  log(aMsg)

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
