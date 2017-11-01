"""Module docstring.

WLC Base Class

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

from sdcp import PackageContainer as PC
from generic import GenericDevice
from netsnmp import VarList, Varbind, Session

################################ WLC Object #####################################
#
# Simpler WLC class
#

class Device(GenericDevice):

 @classmethod
 def get_widgets(cls):
  return ['get_switch_table']

 def __init__(self,aIP, aID = None):
  GenericDevice.__init__(self, aIP, aID)
  
 def __str__(self):
  return "WLC - {}".format(GenericDevice.__str__(self))

 def get_type(self):
  return 'wlc'

 def get_switch_table(self):
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
  ret = []
  for res in cssidobjs:
   macbase=res.tag[34:]
   mac = (macbase+"."+res.iid).split(".")
   mac = ":".join(map(lambda x: hex(int(x))[2:],mac))
   try:
    clientname = gethostbyaddr(ipdict[macbase])[0]
   except:
    clientname = "unknown"
   ret.append({'Name':clientname, 'IP':ipdict.get(macbase), 'MAC':mac, 'SSID': res.val})
  return ret
