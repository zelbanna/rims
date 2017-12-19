"""Module docstring.

vCenter Module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"
__type__   = "hypervisor"

from generic import Device as GenericDevice

############################################ AppformixRPC ######################################
#
# AppformixRPC Class
#
class Device(GenericDevice):

 def __init__(self,aIP,aID=None):
  GenericDevice.__init__(self,aIP,aID)

