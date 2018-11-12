"""Juniper MX Router"""
__author__  = "Zacharias El Banna"
__type__    = "network"
__icon__    = "viz-mx.png"
__oid__     = 2636


from .junos import Junos

################################ MX Object #####################################

class Device(Junos):

 @classmethod
 def get_functions(cls):
  return Junos.get_functions()

 def __init__(self,aIP,aCTX):
  Junos.__init__(self, aCTX, aIP)
  self._interfacenames = {}

 def __str__(self):
  return Junos.__str__(self) + " Style:" + str(self._style)

