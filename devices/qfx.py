"""Module docstring.

QFX module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.10.4"
__status__ = "Production"

import sdcp.PackageContainer as PC
from junos import Junos

################################ QFX Object #####################################

class Device(Junos):

 @classmethod
 def get_widgets(cls):
  widgets = ['widget_switch_table']
  widgets.extend(Junos.get_widgets())
  return widgets

 def __init__(self,aIP,aID=None):
  Junos.__init__(self, aIP,aID,'qfx')
  self._style  = 'els'
  self._interfacenames = {}

 def __str__(self):
  return Junos.__str__(self) + " Style:" + str(self._style)

 #
 # should prep for ELS only and send "instance = 'default-instance'" - then id could be retrieved too
 # since grouping is different
 #
 def get_switch_table(self):
  fdblist = []
  try:
   swdata = self._router.rpc.get_ethernet_switching_table_information()
   for vlan in swdata.iter("l2ng-l2ald-mac-entry-vlan"):
    for entry in vlan.iter("l2ng-mac-entry"):
     vlan = entry.find("l2ng-l2-mac-vlan-name").text
     mac  = entry.find("l2ng-l2-mac-address").text     
     interface = entry.find("l2ng-l2-mac-logical-interface").text
     fdblist.append([ vlan, mac, interface, self.get_interface_name(interface) ])
  except Exception as err:
   self.log_msg("System Error - fetching FDB: " + str(err))
  return fdblist

 #
 # Widgets should be self contained - connect, load names etc
 #
 def widget_switch_table(self):
  try:
   if self.connect():
    self.load_interfaces_name()
    fdb = self.get_switch_table()
    self.close()
    print "<DIV CLASS=z-frame><DIV CLASS=z-table>"
    print "<DIV CLASS=thead><DIV CLASS=th>VLAN</DIV><DIV CLASS=th>MAC</DIV><DIV CLASS=th>Interface</DIV><DIV CLASS=th>Description</DIV></DIV>"
    print "<DIV CLASS=tbody>"
    for n in fdb:
     print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV>".format(n[0],n[1],n[2])
     print "<DIV CLASS=td>{}</DIV>".format(n[3]) if n[3] else "<DIV CLASS=td style='border: 1px solid red'>No Description</DIV>"
     print "</DIV>"
    print "</DIV></DIV></DIV>"
   else:
    print "Could not connect"
  except Exception as err:
   self.log_msg("QFX widget switch table: Error [{}]".format(str(err)))
   print "<B>Error - issue loading widget: {}</B>".format(str(err))
