"""vCenter"""
__author__ = "Zacharias El Banna"
__type__   = "hypervisor"
__oid__     = 6876

from rims.devices.generic import Device as GenericDevice

class Device(GenericDevice):

 def __init__(self, aRT, aID, aIP = None):
  GenericDevice.__init__(self, aRT, aID, aIP)
