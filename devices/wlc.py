"""Juniper WLC"""
__author__  = "Zacharias El Banna"
__type__    = "network"
__oid__     = 14525

from .generic import Device as GenericDevice
from rims.core.common import VarList, Varbind, Session

################################ WLC Object #####################################
#
# Simpler WLC class
#

class Device(GenericDevice):

 @classmethod
 def get_functions(cls):
  return ['switch_table']

 def __init__(self,aIP, aCTX):
  GenericDevice.__init__(self, aIP, aCTX)
  
 def __str__(self):
  return "WLC - {}".format(GenericDevice.__str__(self))

 def switch_table(self):
  from socket import gethostbyaddr
  try:
   # Length of below is used to offset ip address (32) + 1 and mac base (33) + 1 
   cssidobjs = VarList(Varbind(".1.3.6.1.4.1.14525.4.4.1.1.1.1.15"))
   cipobjs = VarList(Varbind(".1.3.6.1.4.1.14525.4.4.1.1.1.1.4"))
   session = Session(Version = 2, DestHost = self._ip, Community = self._ctx.settings['snmp']['read'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.walk(cssidobjs)
   session.walk(cipobjs)
  except:
   return
        
  ipdict= dict((res.tag[33:], res.val.decode()) for res in cipobjs)
  ret = []
  for res in cssidobjs:
   macbase=res.tag[34:]
   mac = (macbase+"."+res.iid).split(".")
   mac = ":".join(hex(int(x))[2:] for x in mac)
   try:
    clientname = gethostbyaddr(ipdict[macbase])[0]
   except:
    clientname = "unknown"
   ret.append({'Name':clientname, 'IP':ipdict.get(macbase), 'MAC':mac, 'SSID': res.val.decode()})
  return ret
