"""NoDHCP API module. Implements dummy DHCP server

"""
__author__ = "Zacharias El Banna"
__version__ = "4.0GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)
__type__ = "DHCP"

#
#
#
def status(aDict):
 """Function docstring for leases. No OP

 Args:
  - type (required)

 Output:
  - data
 """
 return {'data':None }

#
def sync(aDict):
 """No OP

 Args:
  - id (required). Server id on master node

 Output:
  - code. (error code, optional)
  - output. (output from command)
  - result. (operation result)
 """
 return {'output':'No OP','result':'OK'}
