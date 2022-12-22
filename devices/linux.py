"""Linux Device"""
__author__  = "Zacharias El Banna"
__type__    = "os"
__icon__    = "viz-generic.png"
__oid__     = 8072

from rims.devices.generic import Device as GenericDevice

class Device(GenericDevice):

 @classmethod
 def get_data_points(cls):
  return [
   ('chassis','cpu=cpu','CPU free','.1.3.6.1.4.1.2021.11.11.0')
  ]

 def __init__(self, aRT, aID, aIP = None):
  GenericDevice.__init__(self, aRT, aID, aIP)
