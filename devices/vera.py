"""Module docstring.

Vera Library

"""
__author__  = "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__  = "Production"
__type__    = "controller"

from ..devices.generic import Device as GenericDevice

class Device(GenericDevice):

 def __init__(self,aIP,aID=None):
  GenericDevice.__init__(self,aIP,aID)

 @classmethod
 def get_functions(cls):
  return ['manage']

 def __str__(self):
  return "Controller[{}]".format(self._ip)
 
 def call(self,port,query,args = None, method = None):
  from ..core.rest import call as rest_call
  return rest_call("http://%s:%i/data_request?%s"%(self._ip,port,query), aArgs=args, aMethod=method)
