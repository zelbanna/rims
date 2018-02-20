"""Module docstring.

Opengear REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__ = "Production"

#
#
def inventory(aDict):
 """Function docstring for inventory TBD

 Args:
  - ip (required)

 Extra:
 """
 from ..devices.opengear import Device
 ret = {}
 console = Device(aDict['ip'])
 return console.get_inventory()
