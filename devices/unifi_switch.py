"""Ubiquiti Unifi Switch with it's messy snmp walk behavior"""
__author__  = "Zacharias El Banna"
__type__    = "network"
__icon__    = "viz-ex.png"
__oid__     = 8072

from rims.devices.generic import Device as GenericDevice
from easysnmp import Session

def mac_bin_to_hex(inc_bin_mac_address):
  octets = [ord(c) for c in inc_bin_mac_address]
  return "{:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X}".format(*octets)

class Device(GenericDevice):

 def __init__(self, aRT, aID, aIP = None):
  GenericDevice.__init__(self, aRT, aID, aIP)

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
   session = Session(version = 2, hostname = self._ip, community = self._rt.config['snmp']['read'], use_numeric = True, timeout = int(self._rt.config['snmp'].get('timeout',3)), retries = 2)
   with self._rt.snmplock:
    macs = session.walk('.1.3.6.1.2.1.2.2.1.6')
    for mac in macs:
     entry = session.get(['.1.3.6.1.2.1.2.2.1.2.%s'%mac.oid_index,'.1.3.6.1.2.1.2.2.1.8.%s'%mac.oid_index,'.1.3.6.1.2.1.31.1.1.1.18.%s'%mac.oid_index])
     interfaces[int(mac.oid_index)] = {'class':'wired','mac':mac_bin_to_hex(mac.value) if mac.value else "00:00:00:00:00:00", 'name':self.name_decode(entry[0].value),'state':'up' if entry[1].value == '1' else 'down','description':entry[2].value if entry[2].snmp_type != 'NOSUCHINSTANCE' else "None"}
  except Exception as e:
   self.log(str(e))
  return interfaces

 def interface(self, aIndex):
  try:
   session = Session(version = 2, hostname = self._ip, community = self._rt.config['snmp']['read'], use_numeric = True, timeout = int(self._rt.config['snmp'].get('timeout',3)), retries = 2)
   with self._rt.snmplock:
    entry = session.get(['.1.3.6.1.2.1.2.2.1.2.%s'%mac.oid_index,'.1.3.6.1.2.1.2.2.1.8.%s'%mac.oid_index,'.1.3.6.1.2.1.31.1.1.1.18.%s'%mac.oid_index])
  except Exception as e:
   ret = {'status':'NOT_OK','info':repr(e)}
  else:
   ret = {'status':'OK','data':{'mac':mac_bin_to_hex(entry[2].value) if entry[2].value else "00:00:00:00:00:00", 'name':self.name_decode(entry[0].value), 'description':entry[1].value if entry[1].value != "" else "None"}}
  return ret
