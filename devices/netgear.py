"""Netgear switch"""
__author__  = "Zacharias El Banna"
__type__    = "network"
__icon__    = "viz-ex.png"
__oid__     = 4526

from rims.devices.generic import Device as GenericDevice

######################################## Netgear ########################################

class Device(GenericDevice):

 def __init__(self, aCTX, aID, aIP = None):
  GenericDevice.__init__(self, aCTX, aID, aIP)

 def interfaces(self):
  interfaces = super(Device,self).interfaces()
  for k,v in interfaces.items():
   v['name'] = "g%s"%k
  return interfaces
