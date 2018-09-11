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

 def configuration(self,argdict):
  output = ["No config template for this device type.","",
   "Please set the following manually:",
   "- Username: %s"%SC['netconf']['username'],
   "- Password: %s"%SC['netconf']['password'],
   "- Domain:   %s"%argdict['domain'],
   "- Nameserver: %s"%SC['netconf']['dnssrv'],
   "- NTP: %s"%SC['netconf']['ntpsrv'],
   "- Gateway: %s"%argdict['gateway'],
   "- Network/Mask: %s/%s"%(argdict['network'],argdict['mask']),
   "- SNMP read community: %s"%SC['snmp']['read_community'],
   "- SNMP write community: %s"%SC['snmp']['write_community']]
  return output

 def interfaces(self):
  from zdcp.SettingsContainer import SC
  from netsnmp import VarList, Varbind, Session
  interfaces = {}
  try:
   objs = VarList(Varbind('.1.3.6.1.2.1.2.2.1.2'),Varbind('.1.3.6.1.2.1.31.1.1.1.18'))
   session = Session(Version = 2, DestHost = self._ip, Community = SC['snmp']['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.walk(objs)
   for entry in objs:
    intf = interfaces.get(int(entry.iid),{'name':"None",'description':"None"})
    if entry.tag == '.1.3.6.1.2.1.2.2.1.2':
     intf['name'] = entry.val
    if entry.tag == '.1.3.6.1.2.1.31.1.1.1.18':
     intf['description'] = entry.val if entry.val != "" else "None"
    interfaces[int(entry.iid)] = intf
  except Exception as exception_error:
   self.log_msg("Generic : error traversing interfaces: " + str(exception_error))
  return interfaces

 def detect(self):
  ret = {}
  from zdcp.SettingsContainer import SC
  from netsnmp import VarList, Varbind, Session
  try:
   # .1.3.6.1.2.1.1.1.0 : Device info
   # .1.3.6.1.2.1.1.5.0 : Device name
   devobjs = VarList(Varbind('.1.3.6.1.2.1.1.1.0'), Varbind('.1.3.6.1.2.1.1.5.0'))
   session = Session(Version = 2, DestHost = self._ip, Community = SC['snmp']['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.get(devobjs)
   ret['result'] = "OK" if (session.ErrorInd == 0) else "NOT_OK"
  except Exception as err:
   ret['snmp'] = "Not able to do SNMP lookup (check snmp -> read_community): %s"%str(err)
  else:
   ret['info'] = {'model':'unknown', 'type':'generic','snmp':devobjs[1].val.lower() if devobjs[1].val else 'unknown'}
   if devobjs[0].val:
    infolist = devobjs[0].val.split()
    if infolist[0] == "Juniper":
     if infolist[1] == "Networks,":
      ret['info']['model'] = infolist[3].lower()
      for tp in [ 'ex', 'srx', 'qfx', 'mx', 'wlc' ]:
       if tp in ret['info']['model']:
        ret['info']['type'] = tp
        break
     else:
      subinfolist = infolist[1].split(",")
      ret['info']['model'] = subinfolist[2]
    elif infolist[0] == "VMware":
     ret['info']['model'] = "esxi"
     ret['info']['type']  = "esxi"
    elif infolist[0] == "Linux":
     ret['info']['model'] = 'debian' if "Debian" in devobjs[0].val else 'generic'
    else:
     ret['info']['model'] = " ".join(infolist[0:4])
  return ret
