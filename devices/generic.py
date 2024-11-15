"""Generic Device

Relies on SNMP configuration:
 - snmp/read: read community
 - snmp/write: write community
 - snmp/timeout: timeout in seconds, default to 3 seconds

"""
__author__  = "Zacharias El Banna"
__type__    = "generic"
__icon__    = "viz-generic.png"
__oid__     = 8072

from easysnmp import Session
from pythonping import ping
from sys import stderr

def mac_bin_to_hex(inc_bin_mac_address):
  octets = [ord(c) for c in inc_bin_mac_address]
  return "{:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X}".format(*octets)

########################################### Device ########################################
class Device(object):

 def __init__(self, aRT, aID, aIP = None):
  self._id = aID
  self._rt = aRT
  self._ip = aIP if aIP else aRT.node_function(aRT.node if aRT.db else 'master','device','management')({'id':aID})['data']['ip']
  if self._ip is None:
   raise Exception('GenericDevice(%s) - No IP passed or could be found'%aID)

 @classmethod
 def get_functions(cls): return []

 @classmethod
 def get_data_points(cls): return []

 def __str__(self):   return "GenericDevice(id=%s,ip=%s)"%(self._id,self._ip)

 def __enter__(self): return self

 def __exit__(self, *ctx_info): pass

 def log(self, aMsg): self._rt.log(f'DEVICE_LOG({self._id}): {aMsg}')

 def get_ip(self): return self._ip

 def rebind(self, aID, aIP):
  self._ip = aIP
  self._id = aID

 def operation(self, aType):
  self.log("Operation not implemented: %s"%aType)
  return 'NOT_IMPLEMENTED_%s'%aType.upper()

 def ping_device(self):
  return ping(self.ip, verbose=False, count=1, timeout=1).success()

 def configuration(self,argdict):
  ret = ["No config template for this device type.","",
   "Please set the following manually:",
   "- Username: %s"%self._rt.config['netconf']['username'],
   "- Password: %s"%self._rt.config['netconf']['password'],
   "- Domain:   %s"%argdict['domain'],
   "- Gateway: %s"%argdict['gateway'],
   "- Network/Mask: %s/%s"%(argdict['ip'],argdict['mask']),
   "- SNMP network: %s"%self._rt.config['snmp']['network'],
   "- SNMP read community: %s"%self._rt.config['snmp']['read'],
   "- SNMP write community: %s"%self._rt.config['snmp']['write']]

  if self._rt.config.get('tacplus'):
   ret.append("- Tacacs: %s"%self._rt.config['tacplus']['ip'])
  if self._rt.config['netconf'].get('dns'):
   ret.append('- Nameserver: %s'%(self._rt.config['netconf']['dns']))
  if self._rt.config['netconf'].get('ntp'):
   ret.append('- NTP: %s'%(self._rt.config['netconf']['ntp']))
  if self._rt.config['netconf'].get('anonftp'):
   ret.append('- AnonFTP: %s'%(self._rt.config['netconf']['anonftp']))
  return ret

 #
 def interfaces(self):
  interfaces = {}

  session = Session(version = 2, hostname = self._ip, community = self._rt.config['snmp']['read'], use_numeric = True, timeout = int(self._rt.config['snmp'].get('timeout',3)), retries = 2)
  with self._rt.snmplock:
   objs = session.walk(['.1.3.6.1.2.1.2.2.1.6','.1.3.6.1.2.1.2.2.1.2','.1.3.6.1.2.1.2.2.1.8','.1.3.6.1.2.1.31.1.1.1.18'])

  for entry in objs:
   if   entry.oid == '.1.3.6.1.2.1.2.2.1.6':
    interfaces[int(entry.oid_index)] = {'mac':mac_bin_to_hex(entry.value) if entry.value else "00:00:00:00:00:00", 'name':"None",'description':"None",'state':'unknown'}
   elif entry.oid == '.1.3.6.1.2.1.2.2.1.2':
    interfaces[int(entry.oid_index)]['name'] = entry.value
    interfaces[int(entry.oid_index)]['class'] = "wired"
   elif entry.oid == '.1.3.6.1.2.1.2.2.1.8':
    interfaces[int(entry.oid_index)]['state'] = 'up' if entry.value == '1' else 'down'
   elif entry.oid == '.1.3.6.1.2.1.31.1.1.1.18':
    interfaces[int(entry.oid_index)]['description'] = entry.value if entry.value != '' else 'None'
  return interfaces

 #
 def interface(self,aIndex):
  try:
   session = Session(version = 2, hostname = self._ip, community = self._rt.config['snmp']['read'], use_numeric = True, timeout = int(self._rt.config['snmp'].get('timeout',3)), retries = 2)
   with self._rt.snmplock:
    ifoid   = session.get(['.1.3.6.1.2.1.2.2.1.2.%s'%aIndex,'.1.3.6.1.2.1.31.1.1.1.18.%s'%aIndex,'.1.3.6.1.2.1.2.2.1.6.%s'%aIndex])
  except: return {'name':None,'description':None, 'mac':None}
  else:   return {'name':ifoid[0].value,'description':ifoid[1].value if ifoid[1].value != "" else "None", 'mac':mac_bin_to_hex(ifoid[2].value)}

 #
 def interfaces_state(self):
  try:
   session = Session(version = 2, hostname = self._ip, community = self._rt.config['snmp']['read'], use_numeric = True, timeout = int(self._rt.config['snmp'].get('timeout',3)), retries = 2)
   with self._rt.snmplock:
    objs = session.walk('.1.3.6.1.2.1.2.2.1.8')
  except:
   return {}
  else:
   return {int(entry.oid_index):'up' if entry.value == '1' else 'down' for entry in objs if entry.oid_index}

 #
 def data_points(self, aGeneric, aInterfaces, aRemove = True):
  """ Function processes and updates:
   - a list of generic objects containing 'values' which is a list of objects containing (at least) 'oid' which is a complete
   - a list of objects containing 'snmp_index' and use IF-MIB to correlate

   - Will remove unused entries from reporting
  """
  ret = {}
  remove = []
  try:
   session = Session(version = 2, hostname = self._ip, community = self._rt.config['snmp']['read'], use_numeric = True, timeout = int(self._rt.config['snmp'].get('timeout',3)), retries = 2)
   for iif in aInterfaces:
    with self._rt.snmplock:
     ifentry = session.get(['.1.3.6.1.2.1.2.2.1.10.%i'%iif['snmp_index'],'.1.3.6.1.2.1.2.2.1.11.%i'%iif['snmp_index'],'.1.3.6.1.2.1.2.2.1.16.%i'%iif['snmp_index'],'.1.3.6.1.2.1.2.2.1.17.%i'%iif['snmp_index']])
    try:
     iif.update({'in8s':int(ifentry[0].value),'inUPs':int(ifentry[1].value),'out8s':int(ifentry[2].value),'outUPs':int(ifentry[3].value)})
    except Exception as e:
     if ifentry[0].snmp_type == 'NOSUCHINSTANCE':
      self.log(f"generic_data_point => {iif['snmp_index']} scheduled for removal (NOSUCHINSTANCE & {str(e)})")
      remove.append(iif)
     else:
      self.log(f"generic_data_point =>  convertion not ok for index {iif['snmp_index']}")
     iif.update({'in8s':0,'inUPs':0,'out8s':0,'outUPs':0})
   if aRemove:
    for iif in remove:
     aInterfaces.remove(iif)
   for measurement in aGeneric:
    # Wrap all data with the same tag into the same session object
    with self._rt.snmplock:
     objs = session.get([o['oid'] for o in measurement['values']])
    for i,o in enumerate(measurement['values']):
     o['value'] = objs[i].value if objs[i].value else None
  except Exception as e:
   ret['status'] = 'NOT_OK'
   ret['info'] = str(e)
  else:
   ret['status'] = 'OK'
  return ret

#
 def lldp(self):
  # types = {4:"ChassisSubType", 6:"PortIdSubType", 5:"Chassis Id",7:"PortId", 9:"SysName", 8: "PortDesc"}
  # Types defined in 802.1AB-2005
  def hex2ascii(aHex):
   return ':'.join("%s%s"%x for x in zip(*[iter(aHex.hex())]*2))

  def hex2ip(aHex):
   return '.'.join(str(int("0x%s%s"%x,0)) for x in zip(*[iter(aHex.hex())]*2))

  neighbors = {}
  try:
   session = Session(version = 2, hostname = self._ip, community = self._rt.config['snmp']['read'], use_numeric = True, timeout = int(self._rt.config['snmp'].get('timeout',3)), retries = 2)
   with self._rt.snmplock:
    locoid = session.walk('.1.0.8802.1.1.2.1.3.7.1.3')
    remoid = session.walk('.1.0.8802.1.1.2.1.4.1.1')
   for x in locoid:
    neighbors[x.oid_index] = {'snmp_name':x.value,'snmp_index':x.oid_index}
   for entry in remoid:
    parts = entry.oid.split('.')
    n = neighbors.get(parts[-1],{})
    t = parts[11]
    if   t == '4':
     n['chassis_type'] = int(entry.value)
    elif t == '5':
     if n['chassis_type'] == 4:
      if entry.snmp_type == 'OCTETSTR':
       n['chassis_id'] = mac_bin_to_hex(entry.value)
      else:
       n['chassis_id'] = entry.value.lower().replace('-',':')
     elif n['chassis_type'] == 5:
      n['chassis_id'] = hex2ip(entry.value[1:])
     else:
      n['chassis_id'] = entry.value
    elif t == '6':
     n['port_type'] = int(entry.value)
    elif t == '7':
     if n['port_type'] == 3:
      n['port_id'] = mac_bin_to_hex(entry.value)
     else:
      n['port_id'] = entry.value
    elif t == '8':
      n['port_desc'] = "".join(i for i in entry.value if ord(i)<128)
    elif t == '9':
     n['sys_name'] = entry.value
  except Exception as e:
   stderr.write("generic_lldp: Exception -> %s\n"%str(e))
  finally:
   for k in list(neighbors.keys()):
    if not neighbors[k].get('chassis_type'):
     neighbors.pop(k,None)
  return neighbors

 #
 def fdb(self):
  try:
   session = Session(version = 2, hostname = self._ip, community = self._rt.config['snmp']['read'], use_numeric = True, timeout = int(self._rt.config['snmp'].get('timeout',3)), retries = 2)
   with self._rt.snmplock:
    fdb_objs = session.walk('.1.3.6.1.2.1.17.7.1.2.2.1.2')
    int_objs = session.walk('.1.3.6.1.2.1.17.1.4.1.2')
  except Exception as e:
   return {'status':'NOT_OK','info':str(e)}
  else:
   # Map dot1dBasePortIfIndex - interfaces to SNMP index
   baseport = {obj.oid_index:int(obj.value) for obj in int_objs}
   # Map dot1qTpFdbPort - vlan,mac to BasePort
   fdb = []
   for obj in fdb_objs:
    entry = obj.oid[28:].split('.')
    val = 0
    for i in range(1,6):
     val += int(entry[i])
     val = val << 8
    val += int(obj.oid_index)
    bp = obj.value
    fdb.append({'vlan':int(entry[0]),'mac':val,'snmp':baseport.get(bp,int(bp))})
   return {'status':'OK','FDB':fdb}
