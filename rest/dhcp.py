"""DHCP REST module. Translation to correct DHCP server
Settings:
 - node
 - type

 ISC
 - reload (argument from CLI)
 - active (file storing current leases)
 - static (file storing configuration for ISCDHCP

"""
__author__ = "Zacharias El Banna"
__version__ = "18.03.16"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from sdcp.core.common import SC,rest_call

#
#
def update_server(aDict):
 """Function docstring for update_server TBD

 Args:
  - entries (required). entries is a list of dict objects containing hostname, mac, ip etc
  
 Output:
 """
 ret = {}
 if SC['dhcp'].get('node',SC['system']['id']) == SC['system']['id']:
  module = import_module("sdcp.rest.%s"%SC['dhcp']['type'])
  fun = getattr(module,'update_server',None)
  ret = fun(aDict)
 else:
  ret = rest_call("%s?%s_update_server&node=%s"%(SC['node'][SC['dhcp']['node']], SC['dhcp']['type'],SC['dhcp']['node']),aDict)['data']
 return ret             

#
#
def leases(aDict):
 """Function docstring for leases TBD

 Args:
  - type (required)

  Output:
  """
 ret = {}
 if SC['dhcp'].get('node',SC['system']['id']) == SC['system']['id']:
  module = import_module("sdcp.rest.%s"%SC['dhcp']['type'])
  fun = getattr(module,'leases',None)
  ret = fun(aDict)
 else:
  ret = rest_call("%s?%s_leases"%(SC['node'][SC['dhcp']['node']], SC['dhcp']['type'],SC['dhcp']['node']),aDict)['data']
 return ret
