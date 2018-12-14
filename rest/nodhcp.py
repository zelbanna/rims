"""NoDHCP API module. Implements dummy DHCP server"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "DHCP"

#
#
#
def status(aCTX, aArgs = None):
 """Function docstring for leases. No OP

 Args:
  - type (required)

 Output:
  - data
 """
 return {'data':None, 'status':'OK' }

#
def sync(aCTX, aArgs = None):
 """No OP

 Args:
  - id (required). Server id on master node

 Output:
  - code. (error code, optional)
  - output. (output from command)
  - result. (operation result)
 """
 return {'output':'No OP','status':'OK'}

#
#
def restart(aCTX, aArgs = None):
 """Function provides restart capabilities of service

 Args:

 Output:
  - code
  - output
  - result 'OK'/'NOT_OK'
 """
 return {'status':'OK','code':0,'output':""}





