"""Module docstring.

VERA z-wave controller REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

from sdcp.devices.vera import Device

#
# ip
# api
# args
def execute(aDict):
 ctrl = Device(aDict['ip'])
 return ctrl.call(3480,aDict['api'],aDict['args'],aDict['method'])

#
# ip
def status(aDict):
 ctrl = Device(aDict['ip'])
 ret = ctrl.call(3480,"id=sdata")
 ret.pop('header',None)
 ret.pop('code',None)
 return ret

#
# ip
# id (of device)
def dev_info(aDict):
 ctrl = Device(aDict['ip'])
 ret = ctrl.call(3480,"id=status&DeviceNum=%s"%aDict['id'])
 return ret

