"""Ubiquiti Unifi Camera"""
__author__  = "Zacharias El Banna"
__type__    = "network"
__icon__    = "viz-camera.png"
__oid__     = 8072

from rims.devices.generic import Device as GenericDevice

class Device(GenericDevice):

 def __init__(self, aRT, aID, aIP = None):
  GenericDevice.__init__(self, aRT, aID, aIP)
