"""Module docstring.

Module for generic device interaction

"""  
__author__  = "Zacharias El Banna"
__version__ = "17.10.4"
__status__  = "Production"

#
# Returns current list of types
#
def device_types():
 return [ 'ex', 'mx', 'srx', 'qfx', 'wlc', 'linux', 'esxi', 'other', 'unknown', 'pdu', 'console','vcenter']

#
# Returns an instantiation of X type
#
def device_get_instance(aIP,aType):
 try:
  from importlib import import_module
  module = import_module("sdcp.devices.{}".format(aType))
  return getattr(module,'Device',lambda x: None)(aIP)
 except:
  return None

#
#  Return widgets for a give type
#
def device_get_widgets(aType):
 try:
  from importlib import import_module
  module = import_module("sdcp.devices.{}".format(aType))
  Device = getattr(module,'Device',None)
  return Device.get_widgets() if Device else []
 except:
  return []

################################################# Detect #############################################
#
# Detect device info
#
def device_detect(aIP, aDict = {}, aSema = None):
 from sdcp import PackageContainer as PC
 from netsnmp import VarList, Varbind, Session
 from socket import gethostbyaddr
 from sdcp.core import genlib as GL

 if not GL.ping_os(aIP):
  if aSema:
   aSema.release()
  return None

 try:
  # .1.3.6.1.2.1.1.1.0 : Device info
  # .1.3.6.1.2.1.1.5.0 : Device name
  devobjs = VarList(Varbind('.1.3.6.1.2.1.1.1.0'), Varbind('.1.3.6.1.2.1.1.5.0'))
  session = Session(Version = 2, DestHost = aIP, Community = PC.snmp['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
  session.get(devobjs)
 except:
  pass
   
 fqdn,hostname,model,type = 'unknown','unknown','unknown','unknown'
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

 entry = { 'hostname':hostname, 'snmp':snmp, 'model':model, 'type':type, 'fqdn':fqdn  }
 aDict[aIP] = entry
 if aSema:
  aSema.release()
 return entry
