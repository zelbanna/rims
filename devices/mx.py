"""Module docstring.

MX module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"
__type__ = "network"

from junos import Junos

################################ MX Object #####################################

class Device(Junos):

 @classmethod
 def get_widgets(cls):
  return Junos.get_widgets()

 def __init__(self,aIP,aID=None):
  Junos.__init__(self, aIP,aID)
  self._interfacenames = {}

 def __str__(self):
  return Junos.__str__(self) + " Style:" + str(self._style)

