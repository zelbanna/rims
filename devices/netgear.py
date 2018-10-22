"""Netgear switch"""
__author__  = "Zacharias El Banna"
__type__    = "network"
__icon__    = "viz-ex.png"
__oid__     = 4526

from .generic import Device as GenericDevice

######################################## Netgear ########################################

class Device(GenericDevice):

 def __init__(self, aIP, aCTX):
  GenericDevice.__init__(self,aIP, aCTX)

 def __str__(self):
  return "NetGear - {}".format(GenericDevice.__str__(self))

 def interfaces(self):
  interfaces = super(Device,self).interfaces()
  for k,v in interfaces.items():
   v['name'] = "g%s"%k
  return interfaces
