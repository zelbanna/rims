"""Module docstring.

MX module

"""
__author__ = "Zacharias El Banna"
__version__ = "18.03.14GA"
__status__ = "Production"
__type__ = "network"

from junos import Junos

################################ MX Object #####################################

class Device(Junos):

 @classmethod
 def get_functions(cls):
  return Junos.get_functions()

 def __init__(self,aIP,aID=None):
  Junos.__init__(self, aIP,aID)
  self._interfacenames = {}

 def __str__(self):
  return Junos.__str__(self) + " Style:" + str(self._style)

