"""Module docstring.

MX module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.10.4"
__status__ = "Production"

from sdcp import PackageContainer as PC
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

 def get_type(self):
  return 'mx'

