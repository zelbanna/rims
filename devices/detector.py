"""Detector module."""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

from rims.core.common import VarList, Session

################################################### Hardware ###################################################
#
#
def oid41112(aSession, aInfo, aDescription):
 if aDescription[0][0:3] == 'UAP':
  aInfo['type'] = 'unifi_ap'
 else:
  aInfo['type'] = 'unifi_switch'
 try:
  extobj = VarList('.1.3.6.1.4.1.41112.1.6.3.3.0','.1.3.6.1.4.1.41112.1.6.3.6.0')
  aSession.get(extobj)
  aInfo['model']  = extobj[0].val.decode() if extobj[0].val else aDescription[0]
  if extobj[1].val:
   aInfo['version'] = extobj[1].val.decode()
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
   try:
    info['mac'] = int(sysoid[0].val.hex(),16)
   except:
    pass
   # Unifi, but might be others as well encoding MAC as string instead of hex... :-(
   if info['mac'] > 281474976710655:
    try: info['mac'] = int(sysoid[0].val.decode().replace('-',""),16)
    except: pass
  if sysoid[1].val:
   try:
    info['oid'] = int(sysoid[1].val.decode().split('.')[7])
   except:
    pass
  #
  # Device dependendant lookups: devoid, sysoid as arguments, info should merge the result
  #
  if not aBasic:
   info.update({'model':'unknown', 'snmp':'unknown','version':None,'serial':None,'mac':info.get('mac',0),'oid':info.get('oid',0)})
   if devoid[1].val.decode():
    info['snmp'] = devoid[1].val.decode().lower()
   if devoid[2].val.decode():
    try:    enterprise = devoid[2].val.decode().split('.')[7]
    except: enterprise = 0
    infolist = devoid[0].val.decode().split()
    info['oid'] = enterprise
    if enterprise == '12325':
     info['type'] = 'pfsense'
     info['type'] = 'N/A'
     info['version'] = infolist[2]
    elif enterprise == '2636':
     # Juniper
     try:
      extobj = VarList('.1.3.6.1.4.1.2636.3.1.2.0','.1.3.6.1.4.1.2636.3.1.3.0')
      session.get(extobj)
      info['serial'] = extobj[1].val.decode()
      model_list = extobj[0].val.decode().lower().split()
      try: info['model'] = model_list[model_list.index('juniper') + 1]
      except: info['model'] = 'unknown'
      if (info['model']) in ['switch','internet','unknown','virtual']:
       info['model'] = ("%s" if info['model'] != 'virtual' else "%s (VC)")%infolist[3].lower()
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
    elif enterprise == '41112':
     # Unifi
     oid41112(session, info, infolist)
    elif enterprise == '8072':
     # Basic linux, could be any other device...
     info['model'] = ' '.join(infolist[0:4])
     print(devoid[2].val.decode())
     if infolist[0][0:3] == 'UAP':
      oid41112(session, info, infolist)
     else:
      os = {'8':'freebsd','10':'linux','13':'win32','16':'macosx'}.get(devoid[2].val.decode().split('.')[10],'unknown')
      info['type'] = os
    elif enterprise == '4413':
     # Broadcom reference board...
     info['type'] = 'broadcom'
     try:
      extobj = VarList('.1.3.6.1.4.1.4413.1.1.1.1.1.2.0','.1.3.6.1.4.1.4413.1.1.1.1.1.13.0')
      session.get(extobj)
      info['model']  = extobj[0].val.decode() if extobj[0].val else ' '.join(infolist[0:4])
      info['version'] = extobj[1].val.decode()
     except:
      pass
    # Linux
    elif infolist[0] == 'Linux':
     info['model'] = 'debian' if 'Debian' in devoid[0].val.decode() else 'generic'
    else:
     info['model'] = ' '.join(infolist[0:4])
  for k,l in [('model',30),('snmp',20),('version',20),('serial',20)]:
   if info.get(k):
    info[k] = info[k][:l]
 return ret
