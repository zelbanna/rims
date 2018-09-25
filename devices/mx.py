"""Module docstring.

MX module

"""
__author__  = "Zacharias El Banna"
__version__ = "4.0GA"
__status__  = "Production"
__type__    = "network"
__icon__    = "../images/viz-mx.png"
__oid__     = 2636


from junos import Junos

################################ MX Object #####################################

class Device(Junos):

 @classmethod
 def get_functions(cls):
  return Junos.get_functions()

 def __init__(self,aIP,aSettings):
  Junos.__init__(self, aIP, aSettings)
  self._interfacenames = {}

 def __str__(self):
  return Junos.__str__(self) + " Style:" + str(self._style)

