"""Module docstring.

Generic Device

"""
__author__  = "Zacharias El Banna"
__version__ = "18.04.07GA"
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

 def interfaces(self):
  from sdcp.SettingsContainer import SC
  from netsnmp import VarList, Varbind, Session
  interfaces = {}
  try:
   objs = VarList(Varbind('.1.3.6.1.2.1.2.2.1.2'),Varbind('.1.3.6.1.2.1.31.1.1.1.18'))
   session = Session(Version = 2, DestHost = self._ip, Community = SC['snmp']['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.walk(objs)
   for entry in objs:
    intf = interfaces.get(int(entry.iid),{'name':"None",'description':"None"})
    if entry.tag == '.1.3.6.1.2.1.2.2.1.2':
     intf['name'] = entry.val
    if entry.tag == '.1.3.6.1.2.1.31.1.1.1.18':
     intf['description'] = entry.val if entry.val != "" else "None"
    interfaces[int(entry.iid)] = intf
  except Exception as exception_error:
   self.log_msg("Generic : error traversing interfaces: " + str(exception_error))
  return interfaces

