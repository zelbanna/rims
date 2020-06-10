"""Ubiquiti Unifi Switch with it's messy snmp walk behavior"""
__author__  = "Zacharias El Banna"
__type__    = "network"
__icon__    = "viz-ex.png"
__oid__     = 8072

from rims.devices.generic import Device as GenericDevice
from rims.core.common import Session, VarList

class Device(GenericDevice):

 def __init__(self, aCTX, aID, aIP = None):
  GenericDevice.__init__(self, aCTX, aID, aIP)

 # Name decoding according to how LLDP sees 'this' machine
 def name_decode(self, aName):
  name = aName.split()
  if   name[0] == 'Slot:':
   return "%s/%s"%(name[1],name[3])
  elif name[0] == 'Switch':
   return "Port %s"%(name[4])
  elif name[0] == 'CPU' and name[3] == 'Slot:':
   return "irb"
  else:
   return ' '.join(name)

 def interfaces(self):
  interfaces = {}
  try:
   session = Session(Version = 2, DestHost = self._ip, Community = self._ctx.config['snmp']['read'], UseNumeric = 1, Timeout = int(self._ctx.config['snmp'].get('timeout',100000)), Retries = 2)
   macs  = VarList('.1.3.6.1.2.1.2.2.1.6')
   session.walk(macs)
   for mac in macs:
    entry = VarList('.1.3.6.1.2.1.2.2.1.2.%s'%mac.iid,'.1.3.6.1.2.1.2.2.1.8.%s'%mac.iid,'.1.3.6.1.2.1.31.1.1.1.18.%s'%mac.iid)
    session.get(entry)
    interfaces[int(mac.iid)] = {'mac':':'.join("%s%s"%x for x in zip(*[iter(mac.val.hex())]*2)).upper() if mac.val else "00:00:00:00:00:00", 'name':self.name_decode(entry[0].val.decode()),'state':'up' if entry[1].val.decode() == '1' else 'down','description':entry[2].val.decode() if entry[2].val.decode() != "" else "None"}
  except: pass
  return interfaces

 def interface(self, aIndex):
  try:
   session = Session(Version = 2, DestHost = self._ip, Community = self._ctx.config['snmp']['read'], UseNumeric = 1, Timeout = int(self._ctx.config['snmp'].get('timeout',100000)), Retries = 2)
   entry  = VarList('.1.3.6.1.2.1.2.2.1.2.%s'%aIndex,'.1.3.6.1.2.1.31.1.1.1.18.%s'%aIndex,'.1.3.6.1.2.1.2.2.1.6.%s'%aIndex)
   session.get(entry)
  except Exception as e:
   ret = {'status':'NOT_OK','info':repr(e)}
  else:
   ret = {'status':'OK','data':{'mac':':'.join("%s%s"%x for x in zip(*[iter(entry[2].val.hex())]*2)).upper() if entry[2].val else "00:00:00:00:00:00", 'name':self.name_decode(entry[0].val.decode()), 'description':entry[1].val.decode() if entry[1].val.decode() != "" else "None"}}
  return ret
