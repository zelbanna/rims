"""vCenter"""
__author__ = "Zacharias El Banna"
__type__   = "hypervisor"
__oid__     = 6876

from .generic import Device as GenericDevice

############################################ AppformixRPC ######################################
#
# AppformixRPC Class
#
class Device(GenericDevice):

 def __init__(self,aIP, aCTX):
  GenericDevice.__init__(self,aIP, aCTX)

