"""Module docstring.

OpenGear Console module
"""
__author__  = "Zacharias El Banna"
__version__ = "18.04.07GA"
__status__  = "Production"
__type__    = "console"

from generic import Device as GenericDevice

######################################## Console ########################################
#
# Opengear :-)
#

class Device(GenericDevice):

 @classmethod
 def get_functions(cls):
  return ['manage']

 def __init__(self, aIP, aID = None):
  GenericDevice.__init__(self,aIP, aID)

 def __str__(self):
  return "OpenGear - {}".format(GenericDevice.__str__(self))

 def get_inventory(self):
  from netsnmp import VarList, Varbind, Session
  from sdcp.SettingsContainer import SC
  result = []
  try:
   portobjs = VarList(Varbind('.1.3.6.1.4.1.25049.17.2.1.2'))
   session = Session(Version = 2, DestHost = self._ip, Community = SC['snmp']['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.walk(portobjs)
   for obj in portobjs:
    result.append({'interface':obj.iid,'name':obj.val,'port':str(6000+int(obj.iid))})
  except Exception as exception_error:
   self.log_msg("OpenGear : error loading conf " + str(exception_error))
  return result
