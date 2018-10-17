"""NoDHCP API module. Implements dummy DHCP server

"""
__author__ = "Zacharias El Banna"
__version__ = "5.4"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)
__type__ = "DHCP"

#
#
#
def status(aDict, aCTX):
 """Function docstring for leases. No OP

 Args:
  - type (required)

 Output:
  - data
 """
 return {'data':None }

#
def sync(aDict, aCTX):
 """No OP

 Args:
  - id (required). Server id on master node

 Output:
  - code. (error code, optional)
  - output. (output from command)
  - result. (operation result)
 """
 return {'output':'No OP','result':'OK'}

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
 return {'result':'OK','code':0,'output':""}





