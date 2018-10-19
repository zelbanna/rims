"""Vera ZWave"""
__author__  = "Zacharias El Banna"
__type__    = "controller"

from .generic import Device as GenericDevice

class Device(GenericDevice):

 def __init__(self,aIP,aCTX):
  GenericDevice.__init__(self, aIP, aCTX)

 @classmethod
 def get_functions(cls):
  return ['manage']

 def __str__(self):
  return "Controller[{}]".format(self._ip)

