"""Broadcom Device"""
__author__  = "Zacharias El Banna"
__type__    = "os"
__icon__    = "viz-generic.png"
__oid__     = 4413

from rims.devices.generic import Device as GenericDevice

class Device(GenericDevice):

 def __init__(self, aRT, aID, aIP = None):
  GenericDevice.__init__(self, aRT, aID, aIP)
