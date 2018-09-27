"""Module docstring.

Generic Device

"""
__author__  = "Zacharias El Banna"
__version__ = "4.0GA"
__status__  = "Production"
__type__    = "generic"
__icon__    = "../images/viz-generic.png"

############################################# Device ##########################################
class Device(object):

 @classmethod
 def get_functions(cls):
  return []

 def __init__(self, aIP, aSettings):
  self._ip = aIP
  self._settings = aSettings

 def __str__(self):
  return "IP:%s"%(self._ip)

 def __enter__(self):
  return self

 def __exit__(self, *ctx_info):
  pass

 #
 #
 def threading(self, aOperation, aArgs = None):
  try:
   from threading import Thread
   op = getattr(self, aOperation, None)
   thread = Thread(target = op, args=aArgs)
   thread.name = aOperation
   thread.start()
   self.log_msg("threading started: {}({})".format(aOperation,aArgs))
  except:
   self.log_msg("threading error: Illegal operation passed ({})".format(aOperation))
   thread = None
  return thread

 #
 #
 def ping_device(self):
  from os import system
  return system("ping -c 1 -w 1 " + self._ip + " > /dev/null 2>&1") == 0

 #
 #
 def log_msg(self, aMsg):
  from zdcp.core.common import log
  log(aMsg)

 #
 #
 def configuration(self,argdict):
  output = ["No config template for this device type.","",
   "Please set the following manually:",
   "- Username: %s"%self._settings['netconf']['username'],
   "- Password: %s"%self._settings['netconf']['password'],
   "- Domain:   %s"%argdict['domain'],
   "- Nameserver: %s"%self._settings['netconf']['dnssrv'],
   "- NTP: %s"%self._settings['netconf']['ntpsrv'],
   "- Gateway: %s"%argdict['gateway'],
   "- Network/Mask: %s/%s"%(argdict['network'],argdict['mask']),
   "- SNMP read community: %s"%self._settings['snmp']['read_community'],
   "- SNMP write community: %s"%self._settings['snmp']['write_community']]
  return output

 #
 #
 def interfaces(self):
  from binascii import b2a_hex
  from netsnmp import VarList, Varbind, Session
  interfaces = {}
  try:
   objs = VarList(Varbind('.1.3.6.1.2.1.2.2.1.2'),Varbind('.1.3.6.1.2.1.31.1.1.1.18'),Varbind('.1.3.6.1.2.1.2.2.1.8'),Varbind('.1.3.6.1.2.1.2.2.1.6'))
   session = Session(Version = 2, DestHost = self._ip, Community = self._settings['snmp']['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.walk(objs)
   for entry in objs:
    intf = interfaces.get(int(entry.iid),{'name':"None",'description':"None"})
    if entry.tag == '.1.3.6.1.2.1.2.2.1.6':
     intf['mac'] = ":".join(list(b2a_hex(x) for x in list(entry.val))) if entry.val else "00:00:00:00:00:00"
    if entry.tag == '.1.3.6.1.2.1.2.2.1.8':
     intf['state'] = 'up' if entry.val == '1' else 'down'
    if entry.tag == '.1.3.6.1.2.1.2.2.1.2':
     intf['name'] = entry.val
    if entry.tag == '.1.3.6.1.2.1.31.1.1.1.18':
     intf['description'] = entry.val if entry.val != "" else "None"
    interfaces[int(entry.iid)] = intf
  except: pass
  return interfaces

 #
 #
 def interface(self,aIndex):
  from binascii import b2a_hex
  from netsnmp import VarList, Varbind, Session
  try:
   session = Session(Version = 2, DestHost = self._ip, Community = self._settings['snmp']['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   ifoid   = VarList(Varbind('.1.3.6.1.2.1.2.2.1.2.%s'%aIndex),Varbind('.1.3.6.1.2.1.31.1.1.1.18.%s'%aIndex),Varbind('.1.3.6.1.2.1.2.2.1.6.%s'%aIndex))
   session.get(ifoid)
   name,desc = ifoid[0].val,ifoid[1].val if ifoid[1].val != "" else "None"
   mac = ":".join(list(b2a_hex(x) for x in list(ifoid[2].val)))
  except: pass
  return {'name':name,'description':desc, 'mac':mac}

 #
 #
 def lldp(self):
  from netsnmp import VarList, Varbind, Session
  from binascii import b2a_hex
  neighbors = {}
  try:
   session = Session(Version = 2, DestHost = self._ip, Community = self._settings['snmp']['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   locoid = VarList(Varbind('.1.0.8802.1.1.2.1.3.7.1.3'))
   # 4: ChassisSubType, 6: PortIdSubType, 5: Chassis Id, 7: PortId, 9: SysName, 8: PortDesc,10,11,12.. forget
   # Types defined in 802.1AB-2005
   remoid = VarList(Varbind('.1.0.8802.1.1.2.1.4.1.1'))
   session.walk(locoid)
   session.walk(remoid)
   for x in locoid:
    neighbors[x.iid] = {'snmp_name':x.val,'snmp_index':x.iid}
   for entry in remoid:
    parts = entry.tag.split('.')
    n = neighbors.get(parts[-1],{})
    t = parts[11]
    if   t == '4':
     n['chassis_type'] = int(entry.val)
    elif t == '5':
     if n['chassis_type'] == 4:
      n['chassis_id'] = ":".join(list(b2a_hex(x) for x in list(entry.val)))
     elif n['chassis_type'] == 5:
      n['chassis_id'] = ".".join(list(str(int(b2a_hex(x),16)) for x in list(entry.val)[1:]))
     else:
      n['chassis_id'] = entry.val
    elif t == '6':
     n['port_type'] = int(entry.val)
    elif t == '7':
     if n['port_type'] == 3:
      n['port_id'] = ":".join(list(b2a_hex(x) for x in list(entry.val)))
     else:
      n['port_id'] = entry.val
    elif t == '8':
      n['port_desc'] = "".join(i for i in entry.val if ord(i)<128)
    elif t == '9':
     n['sys_name'] = entry.val
  except: pass
  finally:
   for k in neighbors.keys():
    if not neighbors[k].get('chassis_type'):
     neighbors.pop(k,None)
  return neighbors

 #
 #
 def detect(self):
  from netsnmp import VarList, Varbind, Session
  from binascii import b2a_hex
  def hex2ascii(aOctet):
   return ":".join(list(b2a_hex(x) for x in list(aOctet)))

  ret = {'info':{'model':'unknown', 'snmp':'unknown','version':None,'serial':None,'mac':'00:00:00:00:00:00','oid':0}}
  try:
   session = Session(Version = 2, DestHost = self._ip, Community = self._settings['snmp']['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   # Device info, Device name, Enterprise OID
   devoid = VarList(Varbind('.1.3.6.1.2.1.1.1.0'), Varbind('.1.3.6.1.2.1.1.5.0'),Varbind('.1.3.6.1.2.1.1.2.0'))
   sysoid = VarList(Varbind('.1.0.8802.1.1.2.1.3.2.0'))
   session.get(devoid)
   ret['result'] = "OK" if (session.ErrorInd == 0) else "NOT_OK"
   session.get(sysoid)
  except Exception as err:
   ret['result'] = 'NOT_OK'
   ret['error'] = "Not able to do SNMP lookup (check snmp -> read_community): %s"%str(err)
  if ret['result'] == 'OK':
   if sysoid[0].val:
    try: ret['info']['mac'] = hex2ascii(sysoid[0].val)
    except: pass
   if devoid[1].val:
    ret['info']['snmp'] = devoid[1].val.lower()
   if devoid[2].val:
    try:    enterprise = devoid[2].val.split('.')[7]
    except: enterprise = 0
    infolist = devoid[0].val.split()
    ret['info']['oid'] = enterprise
    if enterprise == '2636':
     # Juniper
     try:
      extobj = VarList(Varbind('.1.3.6.1.4.1.2636.3.1.2.0'),Varbind('.1.3.6.1.4.1.2636.3.1.3.0'))
      session.get(extobj)
      ret['info']['serial'] = extobj[1].val
      model_list = extobj[0].val.lower().split()
      try: ret['info']['model'] = model_list[model_list.index('juniper') + 1]
      except: ret['info']['model'] = 'unknown'
      if (ret['info']['model']) in ['switch','internet','unknown','virtual']:
       ret['info']['model'] = ("%s" if not ret['info']['model'] == 'virtual' else "%s (VC)")%infolist[3].lower()
     except: pass
     else:
      for tp in [ 'ex', 'srx', 'qfx', 'mx', 'wlc' ]:
       if tp in ret['info']['model']:
        ret['info']['type'] = tp
        break
     try:    ret['info']['version'] = infolist[infolist.index('JUNOS') + 1][:-1].lower()
     except: pass
    elif enterprise == '14525':
     ret['info']['type'] = 'wlc'
     try:
      extobj = VarList(Varbind('.1.3.6.1.4.1.14525.4.2.1.1.0'),Varbind('.1.3.6.1.4.1.14525.4.2.1.4.0'))
      session.get(extobj)
      ret['info']['serial'] = extobj[0].val
      ret['info']['version'] = extobj[1].val
     except: pass
     ret['info']['model'] = " ".join(infolist[0:4]) 
    elif enterprise == '4526':
     # Netgear
     ret['info']['type'] = 'netgear'
     try:
      extobj = VarList(Varbind('.1.3.6.1.4.1.4526.11.1.1.1.3.0'),Varbind('.1.3.6.1.4.1.4526.11.1.1.1.4.0'),Varbind('.1.3.6.1.4.1.4526.11.1.1.1.13.0'))
      session.get(extobj)
      ret['info']['model']  = extobj[0].val
      ret['info']['serial'] = extobj[1].val
      ret['info']['version'] = extobj[2].val
     except: pass
    elif enterprise == '6876':
     # VMware
     ret['info']['type'] = "esxi"
     try:
      extobj = VarList(Varbind('.1.3.6.1.4.1.6876.1.1.0'),Varbind('.1.3.6.1.4.1.6876.1.2.0'),Varbind('.1.3.6.1.4.1.6876.1.4.0'))
      session.get(extobj)
      ret['info']['model']  = extobj[0].val
      ret['info']['version'] = "%s-%s"%(extobj[1].val,extobj[2].val)
     except: pass
    elif enterprise == '24681':
     ret['info']['type'] = "qnap"
    # Linux
    elif infolist[0] == "Linux":
     ret['info']['model'] = 'debian' if "Debian" in devoid[0].val else 'generic'
    else:
     ret['info']['model'] = " ".join(infolist[0:4])
  else:
   ret['error'] = 'Timeout'
  return ret

