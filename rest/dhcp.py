"""DHCP API module. This module is a REST wrapper for interfaces the DHCP (device) type module."""
__author__ = "Zacharias El Banna"
__version__ = "18.03.07GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from .. import SettingsContainer as SC

#
#
def update_server(aDict):
 """Function docstring for update_server TBD

 Args:

 Output:
 """
 ret = {}
 from ..core.rest import call as rest_call
 macs = rest_call("%s?%device_list_mac"%(SC.node['master'])['data']['entries']
 from importlib import import_module
 module = import_module("sdcp.rest.%s"%SC.dhcp['type'])
 fun = getattr(module,'update_server',None)
 ret = fun({'entries':macs})
 return ret

#
#
def leases(aDict):
 """Function docstring for leases TBD

 Args:
  - type (required)

 Output:
 """
 from importlib import import_module
 module = import_module("sdcp.rest.%s"%SC.dhcp['type'])
 fun = getattr(module,'leases',None)
 ret = fun({'type':aDict['type']})
 return ret
