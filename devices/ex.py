"""Juniper EX switch"""
__author__  = "Zacharias El Banna"
__type__    = "network"
__icon__    = "viz-ex.png"
__oid__     = 2636

from rims.devices.junos import Junos

################################ EX Object #####################################

class Device(Junos):

 def __init__(self, aRT, aID, aIP = None):
  Junos.__init__(self, aRT, aID, aIP)
