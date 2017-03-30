"""Module docstring.

Module for generic device interaction - back end to device-web.cgi

Exports:
- DeviceHandler

"""  
__author__  = "Zacharias El Banna"
__version__ = "1.0GA"
__status__  = "Production"

from sdcp.core.GenLib import DB, ping_os, sys_ips2range, sys_ip2int, sys_int2ip, sys_log_msg

# keys.sort(key=sys_ip2int)
# - Devices is the maintainer of discovered devices, use sys_ip2int as sort key

class Devices(object):

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
 def get_node(cls,aIP,aType):
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
   return Dev(aIP)
  return None                                                              

 def __init__(self):
  self._db = DB()
  self._connected = False

 def connect_db(self):
  self._db.connect()
  self._connected = True
  return self._db
 
 def close_db(self):
  self._db.close()
  self._connected = False

 def get_db(self):
  return self._db

 def get_ip_entry(self,aIP):
  if not self._connected:  
   self._db.connect()
  self._db.do("SELECT * FROM devices WHERE ip = '{}'".format(sys_ip2int(aIP)))
  row = self._db.get_row()
  if not self._connected:
   self._db.close()
  return row

##################################### Device Discovery and Detection ####################################
 #
 # clear existing entries or not?
 def discover(self, aStartIP, aStopIP, aDomain, aClear = False):
  from time import time
  from threading import Thread, BoundedSemaphore
  start_time = int(time())
  sys_log_msg("Device discovery: " + aStartIP + " -> " + aStopIP + ", for domain '" + aDomain + "'")
  self._db.connect()
  db_old, db_new = {}, {}
  if aClear:
   self._db.do("TRUNCATE TABLE devices")
   self._db.commit()
  else:
   self._db.do("SELECT ip FROM devices")
   rows = self._db.get_all_rows()
   for item in rows:
    db_old[item.get('ip')] = True
  try:
   sema = BoundedSemaphore(10)
   for ip in sys_ips2range(aStartIP, aStopIP):
    if db_old.get('ip',None):
     continue
    sema.acquire()
    t = Thread(target = self._detect, args=[ip, aDomain, db_new, sema])
    t.name = "Detect " + ip
    t.start()
   
   # Join all threads by acquiring all semaphore resources
   for i in range(10):
    sema.acquire()

   sql = "INSERT INTO devices (ip,domain,hostname,snmp,model,type,fqdn) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}')"
   for ip,entry in db_new.iteritems():
    self._db.do(sql.format(sys_ip2int(ip),entry['domain'],entry['hostname'],entry['snmp'],entry['model'],entry['type'],entry['fqdn']))
   else:
    self._db.commit()
      
  except Exception as err:
   sys_log_msg("Device discovery: Error [{}]".format(str(err)))
  self._db.close()
  sys_log_msg("Device discovery: Total time spent: {} seconds".format(int(time()) - start_time))
  

 ########################### Detect Devices ###########################
 #
 # Device must answer to ping(!) for system to continue
 #
 # Add proper community handling..
 #
 def _detect(self, aIP, aDomain, aDict = {}, aSema = None):
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

  entry = { 'domain':aDomain, 'hostname':hostname, 'snmp':snmp, 'model':model, 'type':type, 'fqdn':fqdn }
  aDict[aIP] = entry
  if aSema:
   aSema.release()
  return entry

#############################################################################
