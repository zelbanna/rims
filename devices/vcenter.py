"""Module docstring.

vCenter Module

"""
__author__ = "Zacharias El Banna"
__version__ = "1.0GA"
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

