"""SLACK API module. Provides and Interface towards SLACK REST API (webhooks)
Settings under section 'slack':
- 

"""
__author__ = "Zacharias El Banna"
__version__ = "5.2GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)
__type__ = "NOTIFY"

#
#
#
def status(aDict, aCTX):
 """Function docstring for leases TBD

 Args:

 Output:
 """
 return None
#
#
def sync(aDict, aCTX):
 """Function docstring for sync:  reload the DHCP server to use updated info

 Args:
  - id (required). Server id on master node

 Output:
 """
 return None
#
#
def restart(aDict, aCTX):
 """Function provides restart capabilities of service

 Args:

 Output:
  - code
  - output
  - result 'OK'/'NOT_OK'
 """
 return {'code':None, 'output':None, 'result':'OK'}
