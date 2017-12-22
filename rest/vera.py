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
 controller = Device(aDict['ip'])
 return controller.call(3480,aDict['api'],aDict['args'],aDict['method'])['data']

#
# ip
def status(aDict):
 controller = Device(aDict['ip'])
 ret = controller.call(3480,"id=sdata")['data']
 ret.pop('header',None)
 ret.pop('code',None)
 return ret

#
# ip
# id (of device)
def dev_info(aDict):
 controller = Device(aDict['ip'])
 ret = controller.call(3480,"id=status&DeviceNum=%s"%aDict['id'])['data']
 return ret

