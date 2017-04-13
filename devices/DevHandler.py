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
def device_detect(aIP, aDomain, aDict = {}, aSema = None):
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

 entry = { 'domain':aDomain, 'hostname':hostname, 'snmp':snmp, 'model':model, 'type':type, 'fqdn':fqdn, 'rack_size':rack_size }
 aDict[aIP] = entry
 if aSema:
  aSema.release()
 return entry

#################################### Device Discovery and Detection ####################################
#
# clear existing entries or not?

def device_discover(aStartIP, aStopIP, aDomain, aClear = False):
 from time import time
 from threading import Thread, BoundedSemaphore
 start_time = int(time())
 sys_log_msg("Device discovery: " + aStartIP + " -> " + aStopIP + ", for domain '" + aDomain + "'")
 db = DB()
 db.connect()
 db_old, db_new = {}, {}
 if aClear:
  db.do("TRUNCATE TABLE devices")
  db.commit()
 else:
  res  = db.do("SELECT ip FROM devices WHERE ip >= {} and ip <= {}".format(sys_ip2int(aStartIP),sys_ip2int(aStopIP)))
  rows = db.get_all_rows()
  for item in rows:
   db_old[item.get('ip')] = True
 try:
  sema = BoundedSemaphore(10)
  for ip in sys_ips2range(aStartIP, aStopIP):
   if db_old.get(sys_ip2int(ip),None):
    continue
   sema.acquire()
   t = Thread(target = device_detect, args=[ip, aDomain, db_new, sema])
   t.name = "Detect " + ip
   t.start()
  
  # Join all threads by acquiring all semaphore resources
  for i in range(10):
   sema.acquire()
  # We can do insert as either we clear or we skip existing :-)
  sql = "INSERT INTO devices (ip,domain,hostname,snmp,model,type,fqdn,rack_size) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}')"
  for ip,entry in db_new.iteritems():
   db.do(sql.format(sys_ip2int(ip),entry['domain'],entry['hostname'],entry['snmp'],entry['model'],entry['type'],entry['fqdn'],entry['rack_size']))
  else:
   db.commit()
      
 except Exception as err:
  sys_log_msg("Device discovery: Error [{}]".format(str(err)))
 db.close()
 sys_log_msg("Device discovery: Total time spent: {} seconds".format(int(time()) - start_time))
