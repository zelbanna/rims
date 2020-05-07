"""NoDHCP API module. Implements dummy DHCP server"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "DHCP"

#
#
#
def status(aCTX, aArgs):
 """Function docstring for leases. No OP

 Args:
  - type (required)

 Output:
  - data
 """
 return {'data':None, 'status':'OK' }

#
def sync(aCTX, aArgs):
 """No OP

 Args:
  - id (required). Server id on master node

 Output:
  - code. (error code, optional)
  - output. (output from command)
  - status. (operation result)
 """
 return {'status':'OK','output':'No OP'}

#
#
def restart(aCTX, aArgs):
 """Function provides restart capabilities of service

 Args:

 Output:
  - code
  - output
  - result 'OK'/'NOT_OK'
 """
 return {'status':'OK','code':0,'output':""}





