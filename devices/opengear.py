"""Module docstring.

OpenGear Console module
"""  
__author__  = "Zacharias El Banna"
__version__ = "17.10.4"
__status__  = "Production"

from generic import GenericDevice, ConfObject
import sdcp.PackageContainer as PC

######################################## Console ########################################
#
# Opengear :-)
#

class Device(GenericDevice, ConfObject):

 def __init__(self, aIP, aID = None):
  GenericDevice.__init__(self,aIP, aID,'opengear')
  ConfObject.__init__(self)

 def __str__(self):
  return "OpenGear - {}".format(GenericDevice.__str__(self))

 def load_snmp(self):
  from netsnmp import VarList, Varbind, Session
  try:
   portobjs = VarList(Varbind('.1.3.6.1.4.1.25049.17.2.1.2'))
   session = Session(Version = 2, DestHost = self._ip, Community = PC.snmp['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.walk(portobjs)
   self._configitems.clear()
   for result in portobjs:
    # [ Port ] = Name
    self._configitems[ int(result.iid) ] = result.val
  except Exception as exception_error:
   self.log_msg("OpenGear : error loading conf " + str(exception_error), aPrint = True)

