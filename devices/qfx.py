"""Juniper QFX Switch"""
__author__  = "Zacharias El Banna"
__type__    = "network"
__icon__    = "viz-ex.png"
__oid__     = 2636


from rims.devices.junos import Junos

################################ QFX Object #####################################

class Device(Junos):

 def __init__(self, aCTX, aID, aIP = None):
  Junos.__init__(self, aCTX, aID, aIP)
