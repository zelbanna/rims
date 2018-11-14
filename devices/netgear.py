"""Netgear switch"""
__author__  = "Zacharias El Banna"
__type__    = "network"
__icon__    = "viz-ex.png"
__oid__     = 4526

from rims.devices.generic import Device as GenericDevice

######################################## Netgear ########################################

class Device(GenericDevice):

 def __init__(self, aCTX, aIP):
  GenericDevice.__init__(self, aCTX, aIP)

 def __str__(self):
  return "NetGear(ip=%s)"%(self._ip)

 def interfaces(self):
  interfaces = super(Device,self).interfaces()
  for k,v in interfaces.items():
   v['name'] = "g%s"%k
  return interfaces
