"""Module docstring.

Module for generic device interaction - back end to device-web.cgi

Exports:
- DeviceHandler

"""  
__author__  = "Zacharias El Banna"
__version__ = "1.0GA"
__status__  = "Production"

from sdcp.core.GenLib import ConfObject, ping_os, sys_ips2range, sys_ip2int, sys_log_msg

# keys.sort(key=sys_ip2int)
# - Devices is the maintainer of discovered devices, use sys_ip2int as sort key

class Devices(ConfObject):

 @classmethod
 def get_widgets(cls,aType):
  if aType in Devices.get_types():
   if   aType == 'ex':
    from Router import EX
    return EX.get_widgets()
   elif aType == 'qfx':
    from Router import QFX
    return QFX.get_widgets()
   elif aType == 'srx':
    from Router import SRX
    return SRX.get_widgets()
   elif aType == 'wlc':
    from Router import WLC
    return WLC.get_widgets()
   elif aType == 'esxi':
    return ['operated']
  return []

 @classmethod
 def get_types(cls):
  return [ 'ex', 'mx', 'srx', 'qfx', 'wlc', 'linux', 'esxi', 'other', 'unknown' ]

 @classmethod
 def get_node(cls,aNode,aType):
  if aType in Devices.get_types():
   Dev = None
   if   aType == 'ex':
    from Router import EX as Dev
   elif aType == 'qfx':
    from Router import QFX as Dev
   elif aType == 'srx':
    from Router import SRX as Dev
   elif aType == 'wlc':
    from Router import WLC as Dev
   elif aType == 'esxi':
    from ESXi  import ESXi as Dev
   return Dev(aNode)
  return None                                                              

 def __init__(self):
  import sdcp.SettingsContainer as SC
  ConfObject.__init__(self, SC.sdcp_devicefile)  
  
 def __str__(self):
  return "Device: {}\n{}".format(self._configfile, self.get_json())
   
 ##################################### Device Discovery and Detection ####################################
 #
 # clear existing entries or not?
 def discover(self, aStartIP, aStopIP, aDomain, aClear = False):
  from time import time
  from threading import Thread, BoundedSemaphore

  start_time = int(time())
  sys_log_msg("Device discovery: " + aStartIP + " -> " + aStopIP + ", for domain '" + aDomain + "'")

  if not aClear and not self._configitems:
   self.load_json()

  try:
   sema = BoundedSemaphore(10)
   for ip in sys_ips2range(aStartIP, aStopIP):
    if aClear:
     self._configitems.pop(ip,None)
    else:
     existing = self._configitems.get(ip,None)
     if existing:
      continue
    sema.acquire()
    t = Thread(target = self._detect, args=[ip, aDomain, sema])
    t.name = "Detect " + ip
    t.start()
   
   # Join all threads by acquiring all semaphore resources
   for i in range(10):
    sema.acquire()
   #  
   self.save_json()  
  except Exception as err:
   sys_log_msg("Device discovery: Error [{}]".format(str(err)))
  sys_log_msg("Device discovery: Total time spent: {} seconds".format(int(time()) - start_time))

 ########################### Detect Devices ###########################
 #
 # Device must answer to ping(!) for system to continue
 #
 # Add proper community handling..
 #
 def _detect(self, aIP, aDomain, aSema):
  import sdcp.SettingsContainer as SC
  from netsnmp import VarList, Varbind, Session
  from socket import gethostbyaddr
  if not ping_os(aIP):
   aSema.release()
   return False

  try:
   # .1.3.6.1.2.1.1.1.0 : Device info
   # .1.3.6.1.2.1.1.5.0 : Device name
   devobjs = VarList(Varbind('.1.3.6.1.2.1.1.1.0'), Varbind('.1.3.6.1.2.1.1.5.0'))
   session = Session(Version = 2, DestHost = aIP, Community = SC.snmp_read_community, UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.get(devobjs)
  except:
   pass
   
  dns,fqdn,model,type = 'unknown','unknown','unknown','unknown'
  snmp = devobjs[1].val.lower() if devobjs[1].val else 'unknown'
  try:
   dns = gethostbyaddr(aIP)[0].split('.')[0].lower()
   fqdn = dns
  except:
   fqdn = snmp
  fqdn = fqdn.split('.')[0] + "." + aDomain if not (aDomain in fqdn) else fqdn

  if devobjs[0].val:
   infolist = devobjs[0].val.split()
   if infolist[0] == "Juniper":
    if infolist[1] == "Networks,":
     model = infolist[3].lower()
     for tp in [ 'ex', 'srx', 'qfx', 'mx', 'wlc' ]:
      if tp in model:
       type = tp
       break
     else:
      type = "other"
    else:
     subinfolist = infolist[1].split(",")
     model = subinfolist[2]
     type  = "other"
   elif infolist[0] == "VMware":
    model = "esxi"
    type  = "esxi"
   elif infolist[0] == "Linux":
    type = "linux"
    if "Debian" in devobjs[0].val:
     model = "debian"
    else:
     model = "generic"
   else:
    type  = "other"
    model = " ".join(infolist[0:4])

  self._configitems[aIP] = { 'domain':aDomain, 'fqdn':fqdn, 'dns':dns, 'snmp':snmp, 'model':model, 'type':type, 'graphed':'no', 'rack':'unknown', 'unit':'unknown', 'consoleport':'unknown', 'power_left':'unknown', 'power_right':'unknown' }
  aSema.release()
  return True

#############################################################################
