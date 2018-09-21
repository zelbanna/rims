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
  return ['info']

 def __init__(self, aIP, aID = None):
  self._id = aID
  self._ip = aIP

 def __str__(self):
  return "IP:%s ID:%s"%(self._ip, self._id)

 def __enter__(self):
  return self

 def __exit__(self, *ctx_info):
  pass

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

 def ping_device(self):
  from os import system
  return system("ping -c 1 -w 1 " + self._ip + " > /dev/null 2>&1") == 0

 def log_msg(self, aMsg):
  from zdcp.core.common import log
  log(aMsg)

 def info(self):
  return [{'version':'N/A','model':'generic'}]

 def configuration(self,argdict):
  from zdcp.Settings import Settings
  output = ["No config template for this device type.","",
   "Please set the following manually:",
   "- Username: %s"%Settings['netconf']['username'],
   "- Password: %s"%Settings['netconf']['password'],
   "- Domain:   %s"%argdict['domain'],
   "- Nameserver: %s"%Settings['netconf']['dnssrv'],
   "- NTP: %s"%Settings['netconf']['ntpsrv'],
   "- Gateway: %s"%argdict['gateway'],
   "- Network/Mask: %s/%s"%(argdict['network'],argdict['mask']),
   "- SNMP read community: %s"%Settings['snmp']['read_community'],
   "- SNMP write community: %s"%Settings['snmp']['write_community']]
  return output

 def interfaces(self):
  from zdcp.Settings import Settings
  from netsnmp import VarList, Varbind, Session
  interfaces = {}
  try:
   objs = VarList(Varbind('.1.3.6.1.2.1.2.2.1.2'),Varbind('.1.3.6.1.2.1.31.1.1.1.18'),Varbind('.1.3.6.1.2.1.2.2.1.8'))
   session = Session(Version = 2, DestHost = self._ip, Community = Settings['snmp']['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.walk(objs)
   for entry in objs:
    intf = interfaces.get(int(entry.iid),{'name':"None",'description':"None"})
    if entry.tag == '.1.3.6.1.2.1.2.2.1.8':
     intf['state'] = 'up' if entry.val == '1' else 'down'
    if entry.tag == '.1.3.6.1.2.1.2.2.1.2':
     intf['name'] = entry.val
    if entry.tag == '.1.3.6.1.2.1.31.1.1.1.18':
     intf['description'] = entry.val if entry.val != "" else "None"
    interfaces[int(entry.iid)] = intf
  except Exception as exception_error:
   self.log_msg("Generic : error traversing interfaces: " + str(exception_error))
  return interfaces

 def lldp(self):
  from binascii import b2a_hex
  from zdcp.Settings import Settings
  from netsnmp import VarList, Varbind, Session
  def hex2ascii(aOctet):
   return ":".join(list(b2a_hex(x) for x in list(aOctet)))
  neighbors = {}
  ret = {'sysmac':'00:00:00:00:00:00','neighbors':neighbors}
  try:
   session = Session(Version = 2, DestHost = self._ip, Community = Settings['snmp']['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   sysoid = VarList(Varbind('.1.0.8802.1.1.2.1.3.2.0'))
   locoid = VarList(Varbind('.1.0.8802.1.1.2.1.3.7.1.4'))
   # RemMac, RemDesc, RemIndx
   remoid = VarList(Varbind('.1.0.8802.1.1.2.1.4.1.1.5'),Varbind('.1.0.8802.1.1.2.1.4.1.1.8'),Varbind('.1.0.8802.1.1.2.1.4.1.1.7'),Varbind('.1.0.8802.1.1.2.1.4.1.1.9'))
   session.get(sysoid)
   session.walk(locoid)
   session.walk(remoid)
   ret['sysmac'] = hex2ascii(sysoid[0].val)
   for x in locoid:
    neighbors[x.iid] = {'local_interface':x.val}
   for entry in remoid:
    parts = entry.tag.split('.')
    n = neighbors.get(parts[-1],{})
    tag = ".".join(parts[0:12])
    if   tag == '.1.0.8802.1.1.2.1.4.1.1.5':
     n['remote_mac'] = hex2ascii(entry.val)
    elif tag == '.1.0.8802.1.1.2.1.4.1.1.7':
     n['remote_identifier'] = entry.val
    elif tag == '.1.0.8802.1.1.2.1.4.1.1.8':
     n['remote_desc'] = entry.val
    elif tag == '.1.0.8802.1.1.2.1.4.1.1.9':
     n['remote_hostname'] = entry.val
    else:
     n['unknown'] = entry.val
  except Exception as exception_error:
   elf.log_msg("Generic : error traversing neighbors: " + str(exception_error))
  return ret

 def sysmac(self):
  from binascii import b2a_hex
  from zdcp.Settings import Settings
  from netsnmp import VarList, Varbind, Session
  def hex2ascii(aOctet):
   return ":".join(list(b2a_hex(x) for x in list(aOctet)))
  ret = {'sysmac':'00:00:00:00:00:00'}
  try:
   session = Session(Version = 2, DestHost = self._ip, Community = Settings['snmp']['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   sysoid = VarList(Varbind('.1.0.8802.1.1.2.1.3.2.0'))
   session.get(sysoid)
   ret['sysmac'] = hex2ascii(sysoid[0].val)
  except Exception as exception_error:
   elf.log_msg("Generic : error finding sysmac: " + str(exception_error))
  return ret

 def detect(self):
  ret = {}
  from zdcp.Settings import Settings
  from netsnmp import VarList, Varbind, Session
  try:
   # .1.3.6.1.2.1.1.1.0 : Device info
   # .1.3.6.1.2.1.1.5.0 : Device name
   # .1.3.6.1.2.1.1.2.0 : Device Enterprise oid :-)
   devobjs = VarList(Varbind('.1.3.6.1.2.1.1.1.0'), Varbind('.1.3.6.1.2.1.1.5.0'),Varbind('.1.3.6.1.2.1.1.2.0'))
   session = Session(Version = 2, DestHost = self._ip, Community = Settings['snmp']['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.get(devobjs)
   ret['result'] = "OK" if (session.ErrorInd == 0) else "NOT_OK"
  except Exception as err:
   ret['snmp'] = "Not able to do SNMP lookup (check snmp -> read_community): %s"%str(err)
  else:
   ret['info'] = {'model':'unknown', 'type':'generic','snmp':devobjs[1].val.lower() if devobjs[1].val else 'unknown','version':None,'serial':None}
   if devobjs[2].val:
    try:    enterprise = devobjs[2].val.split('.')[7]
    except: enterprise = 0
    infolist = devobjs[0].val.split()
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
    elif infolist[0] == "VMware":
     ret['info']['type']  = "esxi"
     try:
      extobj = VarList(Varbind('.1.3.6.1.4.1.6876.1.1.0'),Varbind('.1.3.6.1.4.1.6876.1.2.0'),Varbind('.1.3.6.1.4.1.6876.1.4.0'))
      session.get(extobj)
      ret['info']['model']  = extobj[0].val
      ret['info']['version'] = "%s-%s"%(extobj[1].val,extobj[2].val)
     except: pass
    # Linux
    elif infolist[0] == "Linux":
     ret['info']['model'] = 'debian' if "Debian" in devobjs[0].val else 'generic'
    else:
     ret['info']['model'] = " ".join(infolist[0:4])
  return ret

