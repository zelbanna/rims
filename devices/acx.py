"""Juniper ACX/EVO Router"""
__author__  = "Zacharias El Banna"
__type__    = "network"
__icon__    = "viz-mx.png"
__oid__     = 2636


from rims.devices.junos import Junos

################################ ACX Object #####################################
#

class Device(Junos):

 def __init__(self, aRT, aID, aIP = None):
  Junos.__init__(self, aRT, aID, aIP)
