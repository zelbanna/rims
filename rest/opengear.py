"""Opengear REST module. PRovides interworking with (through SNMP) opengear console server"""
__author__ = "Zacharias El Banna"
__version__ = "18.03.07GA"
__status__ = "Production"

#
#
def inventory(aDict):
 """Function docstring for inventory TBD

 Args:
  - ip (required)

 Output:
 """
 from ..devices.opengear import Device
 ret = {}
 console = Device(aDict['ip'])
 return console.get_inventory()
