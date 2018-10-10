"""Module docstring.

EX Module

"""
__author__  = "Zacharias El Banna"
__version__ = "5.2GA"
__status__  = "Production"
__type__    = "network"
__icon__    = "../images/viz-ex.png"
__oid__     = 2636

from .junos import Junos

################################ EX Object #####################################

class Device(Junos):

 @classmethod
 def get_functions(cls):
  widgets = ['switch_table']
  widgets.extend(Junos.get_functions())
  return widgets

 def __init__(self,aIP, aSettings):
  Junos.__init__(self, aIP, aSettings)
  self._style  = None
  self._interfacenames = {}

 def __str__(self):
  return Junos.__str__(self) + " Style:" + str(self._style)

 #
 # should prep for ELS only and send "instance = 'default-instance'" - then id could be retrieved too
 # since grouping is different
 #
 def switch_table(self):
  fdblist = []
  try:
   self.load_interfaces_name()
   swdata = self._router.rpc.get_ethernet_switching_table_information()
   if swdata.tag == "l2ng-l2ald-rtb-macdb":
    self._style = "ELS"
    for entry in swdata[0].iter("l2ng-mac-entry"):
     vlan = entry.find("l2ng-l2-mac-vlan-name").text
     mac  = entry.find("l2ng-l2-mac-address").text     
     interface = entry.find("l2ng-l2-mac-logical-interface").text
     fdblist.append({'VLAN':vlan, 'MAC':mac, 'Interface':interface, 'Description':self.get_interface_name(interface)})
   elif swdata.tag == "ethernet-switching-table-information":
    self._style = "Legacy"
    for entry in swdata[0].iter("mac-table-entry"):
     vlan = entry.find("mac-vlan").text
     mac  = entry.find("mac-address").text
     interface = entry.find(".//mac-interfaces").text
     if not mac == "*" and not interface == "Router":
      fdblist.append({'VLAN':vlan, 'MAC':mac, 'Interface':interface, 'Description':self.get_interface_name(interface)}) 
  except Exception as err:
   self.log_msg("System Error - fetching FDB: " + str(err))
  return fdblist
