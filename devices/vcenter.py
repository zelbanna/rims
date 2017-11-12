"""Module docstring.

vCenter Module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

from generic import Device as GenericDevice

############################################ AppformixRPC ######################################
#
# AppformixRPC Class
#
class Device(GenericDevice):

 @classmethod 
 def get_type(cls):   
  return 'hypervisor'

 def __init__(self,aIP,aID=None):
  GenericDevice.__init__(self,aIP,aID)
