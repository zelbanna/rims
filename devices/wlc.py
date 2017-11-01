"""Module docstring.

WLC Base Class

"""
__author__ = "Zacharias El Banna"
__version__ = "17.10.4"
__status__ = "Production"

import sdcp.PackageContainer as PC
from generic import GenericDevice
from netsnmp import VarList, Varbind, Session

################################ WLC Object #####################################
#
# Simpler WLC class
#

class Device(GenericDevice):

 @classmethod
 def get_widgets(cls):
  return ['widget_switch_table']

 def __init__(self,aIP, aID = None):
  GenericDevice.__init__(self, aIP, aID)
  
 def __str__(self):
  return "WLC - {}".format(GenericDevice.__str__(self))

 def get_type(self):
  return 'wlc'

 def widget_switch_table(self):
  from socket import gethostbyaddr
  try:
   # Length of below is used to offset ip address (32) + 1 and mac base (33) + 1 
   cssidobjs = VarList(Varbind(".1.3.6.1.4.1.14525.4.4.1.1.1.1.15"))
   cipobjs = VarList(Varbind(".1.3.6.1.4.1.14525.4.4.1.1.1.1.4"))
    
   session = Session(Version = 2, DestHost = self._ip, Community = PC.snmp['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.walk(cssidobjs)
   session.walk(cipobjs)
  except:
   return
        
  ipdict= dict(map(lambda res: (res.tag[33:], res.val) ,cipobjs))
  print "<DIV CLASS=z-frame><DIV CLASS=z-table>"
  print "<DIV CLASS=thead><DIV CLASS=th>Name</DIV><DIV CLASS=th>IP</DIV><DIV CLASS=th>MAC</DIV><DIV CLASS=th>SSid</DIV></DIV>"
  print "<DIV CLASS=tbody>"
  for res in cssidobjs:
   macbase=res.tag[34:]
   mac = (macbase+"."+res.iid).split(".")
   mac = ":".join(map(lambda x: hex(int(x))[2:],mac))
   try:
    clientname = gethostbyaddr(ipdict[macbase])[0]
   except:
    clientname = "unknown"
   print "<DIV CLASS=tr><DIV CLASS=td>" + clientname + "&nbsp;</DIV><DIV CLASS=td>" + ipdict.get(macbase) + "&nbsp;</DIV><DIV CLASS=td>" + mac + "&nbsp;</DIV><DIV CLASS=td>" + res.val + "</DIV></DIV>"
  print "</DIV></DIV></DIV>"
