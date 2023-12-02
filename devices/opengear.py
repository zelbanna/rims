"""OpenGear Console server"""
__author__  = "Zacharias El Banna"
__type__    = "console"

from rims.devices.generic import Device as GenericDevice
from easysnmp import Session

######################################## Console ########################################
#
# Opengear :-)
#

class Device(GenericDevice):

 @classmethod
 def get_functions(cls):
  return ['manage']

 def __init__(self, aRT, aID, aIP = None):
  GenericDevice.__init__(self, aRT, aID, aIP)

 def get_inventory(self):
  result = []
  try:
   session = Session(version = 2, hostname = self._ip, community = self._rt.config['snmp']['read'], use_numeric = True, timeout = int(self._rt.config['snmp'].get('timeout',3)), retries = 2)
   portobjs = VarList(
   session.walk('.1.3.6.1.4.1.25049.17.2.1.2')
   for obj in portobjs:
    result.append({'interface':obj.oid_index,'name':obj.value})
  except Exception as exception_error:
   self.log("Error loading conf " + str(exception_error))
  return result
