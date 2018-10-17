"""Module docstring.

Netgear module

"""
__author__  = "Zacharias El Banna"
__version__ = "5.4"
__status__  = "Production"
__type__    = "network"
__icon__    = "../images/viz-ex.png"
__oid__     = 4526

from .generic import Device as GenericDevice

######################################## Netgear ########################################

class Device(GenericDevice):

 def __init__(self, aIP, aSettings):
  GenericDevice.__init__(self,aIP, aSettings)

 def __str__(self):
  return "NetGear - {}".format(GenericDevice.__str__(self))

 def interfaces(self):
  interfaces = super(Device,self).interfaces()
  for k,v in interfaces.items():
   v['name'] = "g%s"%k
  return interfaces
