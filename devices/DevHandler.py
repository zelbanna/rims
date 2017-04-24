"""Module docstring.

Module for generic device interaction

"""  
__author__  = "Zacharias El Banna"
__version__ = "10.5GA"
__status__  = "Production"

from sdcp.core.GenLib import DB, ping_os, sys_ips2range, sys_ip2int, sys_log_msg

#
# Returns current list of types
#
def device_types():
 return [ 'ex', 'mx', 'srx', 'qfx', 'wlc', 'linux', 'esxi', 'other', 'unknown', 'pdu', 'console']

#
# Returns an instantiation of X type
#
def device_get_instance(aIP,aType):
 Dev = None
 if   aType == 'ex':
  from Router import EX as Dev
 elif aType == 'qfx':
  from Router import QFX as Dev
 elif aType == 'srx':
  from Router import SRX as Dev
 elif aType == 'mx':
  from Router import MX as Dev
 elif aType == 'wlc':
  from Router import WLC as Dev
 elif aType == 'esxi':
  from ESXi  import ESXi as Dev
 return None if not Dev else Dev(aIP)

#
#  Return widgets for a give type
#
def device_get_widgets(aType):
 Dev = None
 if   aType == 'ex':
  from Router import EX as Dev
 elif aType == 'qfx':
  from Router import QFX as Dev
 elif aType == 'srx':
  from Router import SRX as Dev
 elif aType == 'mx':
  from Router import MX as Dev
 elif aType == 'wlc':
  from Router import WLC as Dev
 elif aType == 'esxi':
  from ESXi import ESXi as Dev
 return [] if not Dev else Dev.get_widgets()

#
# Detect device info
#
def device_detect(aIP, aDict = {}, aSema = None):
 import sdcp.SettingsContainer as SC
 from netsnmp import VarList, Varbind, Session
 from socket import gethostbyaddr
 if not ping_os(aIP):
  if aSema:
   aSema.release()
  return None

 try:
  # .1.3.6.1.2.1.1.1.0 : Device info
  # .1.3.6.1.2.1.1.5.0 : Device name
  devobjs = VarList(Varbind('.1.3.6.1.2.1.1.1.0'), Varbind('.1.3.6.1.2.1.1.5.0'))
  session = Session(Version = 2, DestHost = aIP, Community = SC.snmp_read_community, UseNumeric = 1, Timeout = 100000, Retries = 2)
  session.get(devobjs)
 except:
  pass
   
 rack_size,fqdn,hostname,model,type = 1,'unknown','unknown','unknown','unknown'
 snmp = devobjs[1].val.lower() if devobjs[1].val else 'unknown'
 try:   
  fqdn     = gethostbyaddr(aIP)[0]
  hostname = fqdn.partition('.')[0].lower()
 except:
  pass

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

 entry = { 'hostname':hostname, 'snmp':snmp, 'model':model, 'type':type, 'fqdn':fqdn, 'rack_size':rack_size }
 aDict[aIP] = entry
 if aSema:
  aSema.release()
 return entry
