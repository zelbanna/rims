"""Juniper MX Router"""
__author__  = "Zacharias El Banna"
__type__    = "network"
__icon__    = "viz-mx.png"
__oid__     = 2636


from rims.devices.junos import Junos

################################ MX Object #####################################

class Device(Junos):

 @classmethod
 def get_functions(cls):
  return Junos.get_functions()

 def __init__(self, aCTX, aID, aIP = None):
  Junos.__init__(self, aCTX, aID, aIP)
  self._interfacenames = {}
