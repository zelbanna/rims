"""Module docstring.

Netgear module

"""
__author__  = "Zacharias El Banna"
__version__ = "4.0GA"
__status__  = "Production"
__type__    = "network"
__icon__    = "../images/viz-ex.png"

from generic import Device as GenericDevice

######################################## Netgear ########################################

class Device(GenericDevice):

 def __init__(self, aIP, aID = None):
  GenericDevice.__init__(self,aIP, aID)

 def __str__(self):
  return "NetGear - {}".format(GenericDevice.__str__(self))

