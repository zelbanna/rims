"""Detector module."""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

################################################### Hardware ###################################################
#
#
def execute(aIP, aSNMP, aBasic = False, aDecode = False):
 """ Function does detection and mapping

 Output:
  - status
  - info (dependent)
  - data (dependent)
 """
 from rims.core.common import VarList, Session
 ret = {}
 try:
  session = Session(Version = 2, DestHost = aIP, Community = aSNMP['read'], UseNumeric = 1, Timeout = int(aSNMP.get('timeout',100000)), Retries = 2)
  sysoid = VarList('.1.0.8802.1.1.2.1.3.2.0','.1.3.6.1.2.1.1.2.0')
  session.get(sysoid)
  if (session.ErrorInd != 0):
   raise Exception("SNMP_ERROR_%s"%session.ErrorInd)
  if not aBasic:
   # Device info, Device name, Enterprise OID
   devoid = VarList('.1.3.6.1.2.1.1.1.0','.1.3.6.1.2.1.1.5.0','.1.3.6.1.2.1.1.2.0')
   session.get(devoid)
   if (session.ErrorInd != 0):
    raise Exception("SNMP_ERROR_%s"%session.ErrorInd)
 except Exception as err:
  ret['status'] = 'NOT_OK'
  ret['info'] = str(err)
 else:
  ret['status'] = 'OK'
  ret['data'] = info = {}
  if sysoid[0].val:
   try: info['mac'] = int(sysoid[0].val.hex(),16) if not aDecode else ':'.join("%s%s"%x for x in zip(*[iter(sysoid[0].val.hex())]*2)).upper()
   except: pass
  if sysoid[1].val:
   try:    info['oid'] = int(sysoid[1].val.decode().split('.')[7])
   except: pass
  #
  # Device dependendant lookups: devoid, sysoid as arguments, info should merge the result
  #
  if not aBasic:
   info.update({'model':'unknown', 'snmp':'unknown','version':None,'serial':None,'mac':info.get('mac',0 if not aDecode else '00:00:00:00:00:00'),'oid':info.get('oid',0)})
   if devoid[1].val.decode():
    info['snmp'] = devoid[1].val.decode().lower()
   if devoid[2].val.decode():
    try:    enterprise = devoid[2].val.decode().split('.')[7]
    except: enterprise = 0
    infolist = devoid[0].val.decode().split()
    info['oid'] = enterprise
    if enterprise == '2636':
     # Juniper
     try:
      extobj = VarList('.1.3.6.1.4.1.2636.3.1.2.0','.1.3.6.1.4.1.2636.3.1.3.0')
      session.get(extobj)
      info['serial'] = extobj[1].val.decode()
      model_list = extobj[0].val.decode().lower().split()
      try: info['model'] = model_list[model_list.index('juniper') + 1]
      except: info['model'] = 'unknown'
      if (info['model']) in ['switch','internet','unknown','virtual']:
       info['model'] = ("%s" if not info['model'] == 'virtual' else "%s (VC)")%infolist[3].lower()
     except: pass
     else:
      for tp in [ 'ex', 'srx', 'qfx', 'mx' ]:
       if tp in info['model']:
        info['type'] = tp
        break
     try:    info['version'] = infolist[infolist.index('JUNOS') + 1][:-1].lower()
     except: pass
    elif enterprise == '4526':
     # Netgear
     info['type'] = 'netgear'
     try:
      extobj = VarList('.1.3.6.1.4.1.4526.11.1.1.1.3.0','.1.3.6.1.4.1.4526.11.1.1.1.4.0','.1.3.6.1.4.1.4526.11.1.1.1.13.0')
      session.get(extobj)
      info['model']  = extobj[0].val.decode()
      info['serial'] = extobj[1].val.decode()
      info['version'] = extobj[2].val.decode()
     except: pass
    elif enterprise == '6876':
     # VMware
     info['type'] = "esxi"
     try:
      extobj = VarList('.1.3.6.1.4.1.6876.1.1.0','.1.3.6.1.4.1.6876.1.2.0','.1.3.6.1.4.1.6876.1.4.0')
      session.get(extobj)
      info['model']  = extobj[0].val.decode()
      info['version'] = "%s-%s"%(extobj[1].val.decode(),extobj[2].val.decode())
     except: pass
    elif enterprise == '24681':
     info['type'] = "qnap"
     try:
      extobj = VarList('.1.3.6.1.4.1.24681.1.4.1.1.1.1.1.2.1.3.1','.1.3.6.1.4.1.24681.1.4.1.1.1.1.1.2.1.4.1')
      session.get(extobj)
      info['model']  = extobj[0].val.decode()
      info['serial'] = extobj[1].val.decode()
     except: pass
    elif enterprise == '8072':
     info['model'] = ' '.join(infolist[0:4])
     if info['snmp'] == 'ubnt' and info['model'][0:5] == 'Linux':
      info['type'] = 'unifi_switch'
      # Fucked up MAC, saved as string instead of hex
      info['mac'] = sysoid[0].val.decode().replace('-',':') if aDecode else int(sysoid[0].val.decode().replace('-',""),16)
     elif info['model'][0:3] == 'UAP':
      info['type'] = 'unifi_ap'
      try:
       extobj = VarList('.1.3.6.1.4.1.41112.1.6.3.3.0','.1.3.6.1.4.1.41112.1.6.3.6.0')
       session.get(extobj)
       info['model']  = extobj[0].val.decode()
       info['version'] = extobj[1].val.decode()
      except: pass
     else:
      os = {'8':'freebsd','10':'linux','13':'win32','16':'macosx'}.get(devoid[2].val.decode().split('.')[10],'unknown')
      info['type'] = os
    elif enterprise == '4413':
     if infolist[0][0:3] == 'USW':
      info['type'] = 'unifi_switch'
      try:
       extobj = VarList('.1.3.6.1.4.1.4413.1.1.1.1.1.2.0','.1.3.6.1.4.1.4413.1.1.1.1.1.13.0')
       session.get(extobj)
       info['model']  = extobj[0].val.decode()
       info['version'] = extobj[1].val.decode()
      except: pass
     else:
      info['model'] = ' '.join(infolist[0:4])
    # Linux
    elif infolist[0] == 'Linux':
     info['model'] = 'debian' if 'Debian' in devoid[0].val.decode() else 'generic'
    else:
     info['model'] = ' '.join(infolist[0:4])
  for k,l in [('model',30),('snmp',20),('version',20),('serial',20)]:
   if info.get(k):
    info[k] = info[k][:l]
 return ret
