"""DHCP REST module. Translation to correct DHCP server
Settings, section 'dhcp', parameters:
 - node
 - type

 ISC
 - reload (argument for CLI)
 - active (file storing current leases)
 - static (file storing configuration for ISCDHCP

"""
__author__ = "Zacharias El Banna"
__version__ = "18.05.31GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from zdcp.core.common import node_call
from zdcp.SettingsContainer import SC

#
#
def update_server(aDict):
 """Function docstring for update_server TBD

 Args:
  - entries (required). entries is a list of dict objects containing hostname, mac, ip etc
  
 Output:
 """
 return node_call(SC['dhcp']['node'],SC['dhcp']['type'],'update_server',aDict)

#
#
def leases(aDict):
 """Function docstring for leases TBD

 Args:
  - type (required)

  Output:
  """
 return node_call(SC['dhcp']['node'],SC['dhcp']['type'],'leases',aDict)
