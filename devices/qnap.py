"""QNAP Device"""
__author__  = "Zacharias El Banna"
__type__    = "storage"
__icon__    = "viz-generic.png"
__oid__     = 24681

from rims.devices.generic import Device as GenericDevice

class Device(GenericDevice):

 def __init__(self, aCTX, aIP):
  GenericDevice.__init__(self, aCTX, aIP)

 def __str__(self):
  return "QNAP[%s]"%(self._ip)

