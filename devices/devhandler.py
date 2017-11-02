"""Module docstring.

Module for generic device interaction

"""  
__author__  = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__  = "Production"

#
# Returns current list of types
#
def device_types():
 return [ 'ex', 'mx', 'srx', 'qfx', 'wlc', 'linux', 'esxi', 'other', 'unknown', 'pdu', 'console','vcenter']

#
# Returns an instantiation of X type
#
def device_get_instance(aIP,aType):
 try:
  from importlib import import_module
  module = import_module("sdcp.devices.{}".format(aType))
  return getattr(module,'Device',lambda x: None)(aIP)
 except:
  return None

#
#  Return widgets for a give type
#
def device_get_widgets(aType):
 try:
  from importlib import import_module
  module = import_module("sdcp.devices.{}".format(aType))
  Device = getattr(module,'Device',None)
  return Device.get_widgets() if Device else []
 except:
  return []
