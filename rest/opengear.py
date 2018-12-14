"""Opengear REST module. Provides interworking with (through SNMP) opengear console server"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

#
#
def inventory(aCTX, aArgs = None):
 """Function docstring for inventory TBD

 Args:
  - id (required)

 Output:
  - inventory
 """
 from rims.devices.opengear import Device
 console = Device(aCTX, aArgs['id'])
 return {'inventory':console.get_inventory()}
