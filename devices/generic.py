"""Module docstring.

Generic Device

"""
__author__  = "Zacharias El Banna"
__version__ = "18.03.16"
__status__  = "Production"
__type__    = "generic"

class Device(object):

 @classmethod
 def get_functions(cls):
  return []

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
  from sdcp.core.logger import log
  log(aMsg)

 def configuration(self,argdict):
  return ["No config for device"]
