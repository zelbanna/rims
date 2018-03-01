"""Module docstring.

QFX module

"""
__author__  = "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__  = "Production"
__type__    = "network"

from junos import Junos

################################ QFX Object #####################################

class Device(Junos):

 @classmethod
 def get_functions(cls):
  widgets = ['get_switch_table']
  widgets.extend(Junos.get_functions())
  return widgets

 def __init__(self,aIP,aID=None):
  Junos.__init__(self, aIP,aID)
  self._style  = 'els'
  self._interfacenames = {}

 def __str__(self):
  return Junos.__str__(self) + " Style:" + str(self._style)

 def get_switch_table(self):
  fdblist = []
  try:
   self.load_interfaces_name()
   swdata = self._router.rpc.get_ethernet_switching_table_information()
   for vlan in swdata.iter("l2ng-l2ald-mac-entry-vlan"):
    for entry in vlan.iter("l2ng-mac-entry"):
     vlan = entry.find("l2ng-l2-mac-vlan-name").text
     mac  = entry.find("l2ng-l2-mac-address").text     
     interface = entry.find("l2ng-l2-mac-logical-interface").text
     fdblist.append({ 'VLAN':vlan, 'MAC':mac, 'Interface':interface, 'Description':self.get_interface_name(interface) })
  except Exception as err:
   self.log_msg("System Error - fetching FDB: " + str(err))
  return fdblist
