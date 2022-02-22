"""Juniper SRX Module"""
__author__  = "Zacharias El Banna"
__type__    = "network"
__icon__    = "viz-srx.png"
__oid__     = 2636

from rims.devices.junos import Junos

################################ SRX Object #####################################

class Device(Junos):

 def __init__(self, aCTX, aID, aIP = None):
  Junos.__init__(self, aCTX, aID, aIP)
