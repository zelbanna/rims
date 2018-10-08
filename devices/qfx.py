"""Module docstring.

QFX module

"""
__author__  = "Zacharias El Banna"
__version__ = "5.0GA"
__status__  = "Production"
__type__    = "network"
__icon__    = "../images/viz-ex.png"
__oid__     = 2636


from .junos import Junos

################################ QFX Object #####################################

class Device(Junos):

 @classmethod
 def get_functions(cls):
  widgets = ['switch_table']
  widgets.extend(Junos.get_functions())
  return widgets

 def __init__(self,aIP,aSettings):
  Junos.__init__(self, aIP, aSettings)
  self._style  = 'els'
  self._interfacenames = {}

 def __str__(self):
  return Junos.__str__(self) + " Style:" + str(self._style)

 def switch_table(self):
  fdblist = []
  try:
   swdata = self._router.rpc.get_ethernet_switching_table_information()
   for vlan in swdata.iter("l2ng-l2ald-mac-entry-vlan"):
    for entry in vlan.iter("l2ng-mac-entry"):
     vlan = entry.find("l2ng-l2-mac-vlan-name").text
     mac  = entry.find("l2ng-l2-mac-address").text
     interface = entry.find("l2ng-l2-mac-logical-interface").text
     fdblist.append({ 'VLAN':vlan, 'MAC':mac, 'Interface':interface })
  except Exception as err:
   self.log_msg("System Error - fetching FDB: " + str(err))
  return fdblist
