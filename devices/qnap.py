"""Module docstring.

QNAP Device

"""
__author__  = "Zacharias El Banna"
__version__ = "5.4"
__status__  = "Production"
__type__    = "storage"
__icon__    = "../images/viz-generic.png"
__oid__     = 24681

from .generic import Device as GenericDevice

class Device(GenericDevice):

 def __init__(self,aIP,aSettings):
  GenericDevice.__init__(self, aIP, aSettings)

 def __str__(self):
  return "QNAP[%s]"%(self._ip)

