"""Module docstring.

DHCP API module

"""
__author__ = "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__ = "Production"

from .. import SettingsContainer as SC

#
#
def update_server(aDict):
 """Function description for update_server TBD

 Args:

 Extra:
 """
 from device import list_mac
 ret = {}
 macs = list_mac({})
 if SC.dhcp['node'] == 'master':
  from importlib import import_module
  module = import_module("sdcp.rest.%s"%SC.dhcp['type'])
  fun = getattr(module,'update_server',None)
  ret = fun({'entries':macs})
 else:
  from ..core.rest import call
  res = call(SC.node[SC.dhcp['node']],"%s_update_server"%(SC.dhcp['type']),{'entries':macs})
  ret['output'] = res['data']['output']
  ret['res'] = res['info']['x-z-res']
 return ret

#
#
def leases(aDict):
 """Function description for leases TBD

 Args:
  - type (required)

 Extra:
 """
 if SC.dhcp['node'] == 'master':
  from importlib import import_module
  module = import_module("sdcp.rest.%s"%SC.dhcp['type'])
  fun = getattr(module,'leases',None)
  ret = fun({'type':aDict['type']})
 else:
  from ..core.rest import call
  ret = call(SC.node[SC.dhcp['node']], "%s_leases"%(SC.dhcp['type']),{'type':aDict['type']})['data']
 return ret
