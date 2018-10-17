"""Module docstring.

Vera Library

"""
__author__  = "Zacharias El Banna"
__version__ = "5.4"
__status__  = "Production"
__type__    = "controller"

from .generic import Device as GenericDevice

class Device(GenericDevice):

 def __init__(self,aIP,aSettings):
  GenericDevice.__init__(self, aIP, aSettings)

 @classmethod
 def get_functions(cls):
  return ['manage']

 def __str__(self):
  return "Controller[{}]".format(self._ip)

