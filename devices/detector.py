"""Detector module."""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

from easysnmp import Session

def mac_bin_to_hex(inc_bin_mac_address):
  octets = [ord(c) for c in inc_bin_mac_address]
  return "{:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X}".format(*octets)

def mac_bin_to_int(inc_bin_mac_address):
  octets = [ord(c) for c in inc_bin_mac_address]
  return int("{:02X}{:02X}{:02X}{:02X}{:02X}{:02X}".format(*octets),16)


################################################### Hardware ###################################################
#
#
def oid41112(aSession, aInfo, aDescription):
 if aDescription[0][0:3] == 'UAP':
  aInfo['type'] = 'unifi_ap'
 else:
  aInfo['type'] = 'unifi_switch'
 try:
  extobj = aSession.get(['.1.3.6.1.4.1.41112.1.6.3.3.0','.1.3.6.1.4.1.41112.1.6.3.6.0'])
  aInfo['model']  = extobj[0].value if extobj[0].snmp_type !='NOSUCHOBJECT' else aDescription[0]
  if extobj[1].snmp_type != 'NOSUCHOBJECT':
   aInfo['version'] = extobj[1].value
  else:
   for c,f in enumerate(aDescription):
    if f == 'firmware':
     aInfo['version'] = aDescription[c + 1]
     break
 except:
  pass

################################################### Hardware ###################################################
#
#
def execute(aIP, aSNMP, aBasic = False):
 """ Function does detection and mapping

 Output:
  - status
  - info (dependent)
  - data (dependent)
 """
 ret = {}
 try:
  session = Session(version = 2, hostname = aIP, community = aSNMP['read'], use_numeric = True, timeout = int(aSNMP.get('timeout',3)), retries = 2)
  sysoid = session.get(['.1.0.8802.1.1.2.1.3.2.0','.1.3.6.1.2.1.1.2.0'])
  if not aBasic:
   # Device info, Device name, Enterprise OID
   devoid = session.get(['.1.3.6.1.2.1.1.1.0','.1.3.6.1.2.1.1.5.0','.1.3.6.1.2.1.1.2.0'])
 except Exception as err:
  ret['status'] = 'NOT_OK'
  ret['info'] = str(err)
 else:
  ret['status'] = 'OK'
  ret['data'] = info = {}

  if sysoid[0].snmp_type == 'OCTETSTR':
   try:
    info['mac'] = mac_bin_to_int(sysoid[0].value)
   except:
    pass
  elif sysoid[0].snmp_type == 'NOSUCHOBJECT':
   pass
  else:
   raise Exception('MAC_MATCHING_TODO')
  if sysoid[1].value:
   try:
    info['oid'] = int(sysoid[1].value.split('.')[7])
   except:
    pass
  #
  # Device dependendant lookups: devoid, sysoid as arguments, info should merge the result
  #
  if not aBasic:
   info.update({'model':'unknown', 'snmp':'unknown','version':None,'serial':None,'mac':info.get('mac',0),'oid':info.get('oid',0)})
   if devoid[1].value:
    info['snmp'] = devoid[1].value.lower()
   if devoid[2].value:
    try:    enterprise = devoid[2].value.split('.')[7]
    except: enterprise = 0
    infolist = devoid[0].value.split()
    info['oid'] = enterprise
    if enterprise == '12325':
     info['type'] = 'pfsense'
     info['model'] = 'N/A'
     info['version'] = infolist[2]
    elif enterprise == '2636':
     # Juniper
     try:
      extobj = session.get(['.1.3.6.1.4.1.2636.3.1.2.0','.1.3.6.1.4.1.2636.3.1.3.0'])
      info['serial'] = extobj[1].value
      model_list = extobj[0].value.lower().split()
      try:
       info['model'] = model_list[model_list.index('juniper') + 1]
      except:
       info['model'] = 'unknown'
      if (info['model']) in ['switch','internet','unknown','virtual']:
       info['model'] = ("%s" if info['model'] != 'virtual' else "%s (VC)")%infolist[3].lower()
      if info['model'] == "jnp48y8c-chas":
       info['model'] = 'qfx5120-48y'
      elif info['model'] == "jnp204":
       info['model'] = 'mx204'
      elif info['model'] == "jnp10003":
       info['model'] = 'mx10003'
     except:
      pass
     else:
      for tp in [ 'ex', 'srx', 'qfx', 'mx', 'ptx', 'acx']:
       if tp in info['model']:
        info['type'] = tp
        break
     try:
      info['version'] = infolist[infolist.index('JUNOS') + 1][:-1].lower()
     except:
      pass
    elif enterprise == '4526':
     # Netgear
     info['type'] = 'netgear'
     try:
      extobj = session.get(['.1.3.6.1.4.1.4526.11.1.1.1.3.0','.1.3.6.1.4.1.4526.11.1.1.1.4.0','.1.3.6.1.4.1.4526.11.1.1.1.13.0'])
      info['model']  = extobj[0].value
      info['serial'] = extobj[1].value
      info['version'] = extobj[2].value
     except:
      pass
    elif enterprise == '6876':
     # VMware
     info['type'] = "esxi"
     try:
      extobj = session.get(['.1.3.6.1.4.1.6876.1.1.0','.1.3.6.1.4.1.6876.1.2.0','.1.3.6.1.4.1.6876.1.4.0'])
      info['model']  = extobj[0].value
      info['version'] = "%s-%s"%(extobj[1].value,extobj[2].value)
     except:
      pass
    elif enterprise == '24681':
     info['type'] = "qnap"
     try:
      extobj = session.get(['.1.3.6.1.4.1.24681.1.4.1.1.1.1.1.2.1.3.1','.1.3.6.1.4.1.24681.1.4.1.1.1.1.1.2.1.4.1'])
      info['model']  = extobj[0].value
      info['serial'] = extobj[1].value
     except:
      pass
    elif enterprise == '41112':
     # Unifi
     oid41112(session, info, infolist)
    elif enterprise == '8072':
     # Basic linux, could be any other device...
     info['model'] = ' '.join(infolist[0:4])
     print(devoid[2].value)
     if infolist[0][0:3] == 'UAP':
      oid41112(session, info, infolist)
     else:
      os = {'8':'freebsd','10':'linux','13':'win32','16':'macosx'}.get(devoid[2].value.split('.')[10],'unknown')
      info['type'] = os
    elif enterprise == '4413':
     # Broadcom reference board...
     info['type'] = 'broadcom'
     try:
      extobj = session.get(['.1.3.6.1.4.1.4413.1.1.1.1.1.2.0','.1.3.6.1.4.1.4413.1.1.1.1.1.13.0'])
      info['model']  = extobj[0].value if extobj[0].value else ' '.join(infolist[0:4])
      info['version'] = extobj[1].value
     except:
      pass
    # Linux
    elif infolist[0] == 'Linux':
     info['model'] = 'debian' if 'Debian' in devoid[0].value else 'generic'
    else:
     info['model'] = ' '.join(infolist[0:4])
  for k,l in [('model',30),('snmp',20),('version',20),('serial',20)]:
   if info.get(k):
    info[k] = info[k][:l]
 return ret
