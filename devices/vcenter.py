"""Module docstring.

vCenter Module

"""
__author__ = "Zacharias El Banna"
__version__ = "5.2GA"
__status__ = "Production"
__type__   = "hypervisor"
__oid__     = 6876

from .generic import Device as GenericDevice

############################################ AppformixRPC ######################################
#
# AppformixRPC Class
#
class Device(GenericDevice):

 def __init__(self,aIP, aSettings):
  GenericDevice.__init__(self,aIP, aSettings)

