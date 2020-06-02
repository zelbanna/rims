"""Generic Device

Relies on SNMP configuration:
 - snmp/read: read community
 - snmp/write: write community
 - snmp/timeout: timeout in microseconds, default to 100000 micro seconds

"""
__author__  = "Zacharias El Banna"
__type__    = "generic"
__icon__    = "viz-generic.png"
__oid__     = 8072

from rims.core.common import VarList, VarBind, Session

########################################### Device ########################################
class Device(object):

 def __init__(self, aCTX, aID, aIP = None):
  self._id = aID
  self._ctx = aCTX
  self._ip = aIP if aIP else aCTX.node_function('master','device','management')({'id':aID})['data']['ip']
  if self._ip is None:
   raise Exception('GenericDevice(%s) - No IP passed or could be found'%aID)

 @classmethod
 def get_functions(cls): return []

 @classmethod
 def get_data_points(cls): return []

 def __str__(self):   return "GenericDevice(id=%s,ip=%s)"%(self._id,self._ip)

 def __enter__(self): return self

 def __exit__(self, *ctx_info): pass

 def log(self, aMsg): self._ctx.node_function('master','device','log_put')(aArgs = {'message':aMsg[:96], 'id':self._id})

 def get_ip(self): return self._ip

 def rebind(self, aID, aIP):
  self._ip = aIP
  self._id = aID

 def operation(self, aType):
  self.log("Operation not implemented: %s"%aType)
  return 'NOT_IMPLEMENTED_%s'%aType.upper()

 def ping_device(self):
  from os import system
  return system("ping -c 1 -w 1 " + self._ip + " > /dev/null 2>&1") == 0

 def configuration(self,argdict):
  ret = ["No config template for this device type.","",
   "Please set the following manually:",
   "- Username: %s"%self._ctx.config['netconf']['username'],
   "- Password: %s"%self._ctx.config['netconf']['password'],
   "- Domain:   %s"%argdict['domain'],
   "- Gateway: %s"%argdict['gateway'],
   "- Network/Mask: %s/%s"%(argdict['network'],argdict['mask']),
   "- SNMP read community: %s"%self._ctx.config['snmp']['read'],
   "- SNMP write community: %s"%self._ctx.config['snmp']['write']]

  if self._ctx.config.get('tacplus'):
   ret.append("- Tacacs: %s"%self._ctx.config['tacplus']['ip'])
  if self._ctx.config['netconf'].get('dns'):
   ret.append('- Nameserver: %s'%(self._ctx.config['netconf']['dns']))
  if self._ctx.config['netconf'].get('ntp'):
   ret.append('- NTP: %s'%(self._ctx.config['netconf']['ntp']))
  if self._ctx.config['netconf'].get('anonftp'):
   ret.append('- AnonFTP: %s'%(self._ctx.config['netconf']['anonftp']))
  return ret

 #
 def interfaces(self):
  interfaces = {}
  try:
   objs = VarList('.1.3.6.1.2.1.2.2.1.6','.1.3.6.1.2.1.2.2.1.2','.1.3.6.1.2.1.2.2.1.8','.1.3.6.1.2.1.31.1.1.1.18')
   session = Session(Version = 2, DestHost = self._ip, Community = self._ctx.config['snmp']['read'], UseNumeric = 1, Timeout = int(self._ctx.config['snmp'].get('timeout',100000)), Retries = 2)
   session.walk(objs)
   if (session.ErrorInd != 0):
    raise Exception("SNMP_ERROR_%s"%session.ErrorInd)
   for entry in objs:
    if   entry.tag == '.1.3.6.1.2.1.2.2.1.6':
     interfaces[int(entry.iid)] = {'mac':':'.join("%s%s"%x for x in zip(*[iter(entry.val.hex())]*2)).upper() if entry.val else "00:00:00:00:00:00", 'name':"None",'description':"None",'state':'unknown'}
    elif entry.tag == '.1.3.6.1.2.1.2.2.1.2':
     interfaces[int(entry.iid)]['name'] = entry.val.decode()
    elif entry.tag == '.1.3.6.1.2.1.2.2.1.8':
     interfaces[int(entry.iid)]['state'] = 'up' if entry.val.decode() == '1' else 'down'
    elif entry.tag == '.1.3.6.1.2.1.31.1.1.1.18':
     interfaces[int(entry.iid)]['description'] = entry.val.decode() if entry.val.decode() != '' else 'None'
  except: pass
  return interfaces

 #
 def interface(self,aIndex):
  try:
   session = Session(Version = 2, DestHost = self._ip, Community = self._ctx.config['snmp']['read'], UseNumeric = 1, Timeout = int(self._ctx.config['snmp'].get('timeout',100000)), Retries = 2)
   ifoid   = VarList('.1.3.6.1.2.1.2.2.1.2.%s'%aIndex,'.1.3.6.1.2.1.31.1.1.1.18.%s'%aIndex,'.1.3.6.1.2.1.2.2.1.6.%s'%aIndex)
   session.get(ifoid)
  except: return {'name':None,'description':None, 'mac':None}
  else:   return {'name':ifoid[0].val.decode(),'description':ifoid[1].val.decode() if ifoid[1].val.decode() != "" else "None", 'mac':':'.join("%s%s"%x for x in zip(*[iter(ifoid[2].val.hex())]*2)).upper()}

 #
 def interfaces_state(self):
  try:
   objs = VarList('.1.3.6.1.2.1.2.2.1.8')
   session = Session(Version = 2, DestHost = self._ip, Community = self._ctx.config['snmp']['read'], UseNumeric = 1, Timeout = int(self._ctx.config['snmp'].get('timeout',100000)), Retries = 2)
   session.walk(objs)
  except: return {}
  else: return {int(entry.iid):'up' if entry.val.decode() == '1' else 'down' for entry in objs if entry.iid} if (session.ErrorInd == 0) else {}

 #
 def data_points(self, aGeneric, aInterfaces):
  """ Function processes and updates:
   - a list of generic objects containing 'snmp' which is a list of objects containing (at least) 'oid' which is a complete
   - a list of objects containing 'snmp_index' and use IF-MIB to correlate
  """
  ret = {}
  try:
   session = Session(Version = 2, DestHost = self._ip, Community = self._ctx.config['snmp']['read'], UseNumeric = 1, Timeout = int(self._ctx.config['snmp'].get('timeout',100000)), Retries = 2)
   for iif in aInterfaces:
    ifentry = VarList('.1.3.6.1.2.1.2.2.1.10.%i'%iif['snmp_index'],'.1.3.6.1.2.1.2.2.1.11.%i'%iif['snmp_index'],'.1.3.6.1.2.1.2.2.1.16.%i'%iif['snmp_index'],'.1.3.6.1.2.1.2.2.1.17.%i'%iif['snmp_index'])
    session.get(ifentry)
    if (session.ErrorInd != 0):
     raise Exception("SNMP_ERROR_%s"%session.ErrorInd)
    else:
     iif.update({'in8s':int(ifentry[0].val),'inUPs':int(ifentry[1].val),'out8s':int(ifentry[2].val),'outUPs':int(ifentry[3].val)})
   for measurement in aGeneric:
    # Wrap all data with the same tag into the same session object
    objs = VarList(*[o['oid'] for o in measurement['snmp']])
    session.get(objs)
    if (session.ErrorInd != 0):
     raise Exception("SNMP_ERROR_%s"%session.ErrorInd)
    else:
     for i,o in enumerate(measurement['snmp']):
      o['value'] = objs[i].val.decode()
  except Exception as e:
   ret['status'] = 'NOT_OK'
   ret['info'] = str(e)
  else:
   ret['status'] = 'OK'
  return ret

 #
 def lldp(self):
  def hex2ascii(aHex):
   return ':'.join("%s%s"%x for x in zip(*[iter(aHex.hex())]*2))

  def hex2ip(aHex):
   return '.'.join(str(int("0x%s%s"%x,0)) for x in zip(*[iter(aHex.hex())]*2))

  neighbors = {}
  try:
   session = Session(Version = 2, DestHost = self._ip, Community = self._ctx.config['snmp']['read'], UseNumeric = 1, Timeout = int(self._ctx.config['snmp'].get('timeout',100000)), Retries = 2)
   locoid = VarList('.1.0.8802.1.1.2.1.3.7.1.3')
   remoid = VarList('.1.0.8802.1.1.2.1.4.1.1')
   session.walk(locoid)
   session.walk(remoid)
   for x in locoid:
    neighbors[x.iid] = {'snmp_name':x.val.decode(),'snmp_index':x.iid}
   for entry in remoid:
    # 4: ChassisSubType, 6: PortIdSubType, 5: Chassis Id, 7: PortId, 9: SysName, 8: PortDesc,10,11,12.. forget
    # Types defined in 802.1AB-2005
    parts = entry.tag.split('.')
    n = neighbors.get(parts[-1],{})
    t = parts[11]
    if   t == '4':
     n['chassis_type'] = int(entry.val.decode())
    elif t == '5':
     # Check length - ascii encoded hex?
     if n['chassis_type'] == 4:
      if len(entry.val) == 6:
       n['chassis_id'] = hex2ascii(entry.val)
      else:
       n['chassis_id'] = entry.val.decode().lower().replace('-',':')
     elif n['chassis_type'] == 5:
      n['chassis_id'] = hex2ip(entry.val[1:])
     else:
      n['chassis_id'] = entry.val.decode()
    elif t == '6':
     n['port_type'] = int(entry.val.decode())
    elif t == '7':
     if n['port_type'] == 3:
      n['port_id'] = hex2ascii(entry.val)
     else:
      n['port_id'] = entry.val.decode()
    elif t == '8':
      n['port_desc'] = "".join(i for i in entry.val.decode() if ord(i)<128)
    elif t == '9':
     n['sys_name'] = entry.val.decode()
  except:
   pass
  finally:
   for k in list(neighbors.keys()):
    if not neighbors[k].get('chassis_type'):
     neighbors.pop(k,None)
  return neighbors

 #
 def fdb(self):
  try:
   objs = VarList('.1.3.6.1.2.1.17.7.1.2.2.1.2')
   session = Session(Version = 2, DestHost = self._ip, Community = self._ctx.config['snmp']['read'], UseNumeric = 1, Timeout = int(self._ctx.config['snmp'].get('timeout',100000)), Retries = 2)
   session.walk(objs)
  except Exception as e: return {'status':'NOT_OK','info':str(e)}
  else:
   if (session.ErrorInd == 0):
    fdb = []
    for obj in objs:
     entry = obj.tag[28:].split('.')
     val = 0
     for i in range(1,6):
      val += int(entry[i])
      val = val << 8
     val += int(obj.iid)
     fdb.append({'vlan':int(entry[0]),'mac':val,'snmp':int(obj.val.decode())})
    return {'status':'OK','FDB':fdb}
   else:
    return {'status':'NOT_OK','info':'SNMP error: %s'%session.ErrorInd}
