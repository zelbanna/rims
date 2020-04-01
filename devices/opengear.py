"""OpenGear Console server"""
__author__  = "Zacharias El Banna"
__type__    = "console"

from rims.devices.generic import Device as GenericDevice
from rims.core.common import VarList, Session

######################################## Console ########################################
#
# Opengear :-)
#

class Device(GenericDevice):

 @classmethod
 def get_functions(cls):
  return ['manage']

 def __init__(self, aCTX, aID, aIP = None):
  GenericDevice.__init__(self, aCTX, aID, aIP)

 def __str__(self):
  return "OpenGear[%s,%s]"%(self._id,self._ip)

 def get_inventory(self):
  result = []
  try:
   portobjs = VarList('.1.3.6.1.4.1.25049.17.2.1.2')
   session = Session(Version = 2, DestHost = self._ip, Community = self._ctx.config['snmp']['read'], UseNumeric = 1, Timeout = int(self._ctx.config['snmp'].get('timeout',100000)), Retries = 2)
   session.walk(portobjs)
   for obj in portobjs:
    result.append({'interface':obj.iid,'name':obj.val.decode()})
  except Exception as exception_error:
   self.log("Error loading conf " + str(exception_error))
  return result
