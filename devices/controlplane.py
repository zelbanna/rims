"""Control Plane Device"""
__author__  = "Zacharias El Banna"
__version__ = "5.3GA"
__status__  = "Production"
__type__    = "controlplane"

from .generic import Device as GenericDevice

class Device(GenericDevice):

 @classmethod
 def get_functions(cls):
  return []

 def __init__(self, aIP, aSettings):
  GenericDevice.__init__(self,aIP, aSettings)

 def __str__(self):
  return "Control Plane"

 def system_info(self):
  return {}

 def interfaces(self):
  return {}

 def interface(self, aIndex):
  return {'name':None,'description':None, 'mac':None}

 def lldp(self):
  return {}
