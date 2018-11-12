"""Opengear REST module. PRovides interworking with (through SNMP) opengear console server"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

#
#
def inventory(aCTX, aDict):
 """Function docstring for inventory TBD

 Args:
  - ip (required)

 Output:
 """
 from rims.devices.opengear import Device
 console = Device(aCTX,aDict['ip'])
 return console.get_inventory()
