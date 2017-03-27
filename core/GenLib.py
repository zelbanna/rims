"""Module docstring.

Generic Library

"""
__author__ = "Zacharias El Banna"
__version__ = "1.0GA"
__status__ = "Production"

from socket import inet_ntoa, inet_aton

################################# Generic Classes ####################################
#
# Generic Device Class
#
class GenDevice(object):
 
 # set a number of entries:
 # - _ip
 # - _hostname
 # - _domain
 # - _fqdn
 # - _logfile
 
 # Two options:
 # ahost and adomain is set, then FQDN = host.domain and ip is derived
 # if ahost is ip, try to lookup hostname and domain
 #
 # use _ip everywhere we need to connect, use fqdn and domain and host for display purposes
 
 def __init__(self, ahost, adomain = None, atype = "unknown"):
  import sdcp.SettingsContainer as SC
  from socket import gethostbyname, getfqdn
  self._type = atype
  if sys_is_ip(ahost):
   self._ip = ahost
   try:
    self._fqdn = getfqdn(ahost)
    self._hostname = self._fqdn.partition('.')[0]
    self._domain   = self._fqdn.partition('.')[2]
   except:
    self._fqdn = ahost
    self._hostname = ahost
    self._domain = aDomain
  else:
   # ahost is a aname, if domain is not supplied, can it be part of host? 
   if adomain:
    self._fqdn = ahost + "." + adomain
    self._hostname = ahost
    self._domain = adomain
    try:
     self._ip = gethostbyname(self._fqdn)
    except:
     try:
      self._ip = gethostbyname(ahost)
     except:
      self._ip = ahost
   else:
    self._fqdn = ahost
    self._hostname = self._fqdn.partition('.')[0]
    self._domain   = self._fqdn.partition('.')[2]
    try:
     self._ip = gethostbyname(ahost)
    except:
     self._ip = ahost
  if self._domain == "":
   self._domain = None
  self._logfile = SC.sdcp_logformat.format(self._fqdn)

 def __str__(self):
  return "FQDN: {} IP: {} Hostname: {} Domain: {} Type:{}".format(self._fqdn, self._ip, self._hostname, self._domain, self._type)
 
 def ping_device(self):
  return ping_os(self._fqdn)

 def get_type(self):
  return self._type

 def log_msg(self, aMsg, aPrint = False):
  from time import localtime, strftime
  output = unicode("{} : {}".format(strftime('%Y-%m-%d %H:%M:%S', localtime()), aMsg))
  if aPrint:
   print output
  with open(self._logfile, 'a') as f:
   f.write(output + "\n")

#
# Generic Configuration Class
#
class ConfObject(object):

 def __init__(self, aFilename = None):
  self._configitems = {}
  self._filename = aFilename

 def __str__(self):
  return "Configuration: - {}".format(str(self._configitems))

 def load_snmp(self):
  pass

 def load_json(self):
  try:
   self._configitems.clear()
   from json import load as json_load_file
   with open(self._filename) as conffile:
    self._configitems = json_load_file(conffile)
  except:
   pass
   
 def save_json(self):
  from json import dump as json_save_file
  with open(self._filename,'w') as conffile:
    json_save_file(self._configitems, conffile, indent = 1, sort_keys = True)

 def get_json(self):
  from json import dumps as json_get_str
  return json_get_str(self._configitems, indent = 1, sort_keys = True)

 def add_db_position(self, aPos, aVal = 'unknown'):
  self.load_json()
  for entry in self._configitems.itervalues():
   entry[aPos] = aVal
  self.save_json()

 def get_json_to_html(self):
  pass

 def get_keys(self, aTargetName = None, aTargetValue = None, aSortKey = None):
  if not aTargetName:
   keys = self._configitems.keys()
  else:
   keys = []
   for key, entry in self._configitems.iteritems():
    if entry[aTargetName] == aTargetValue:
     keys.append(key)
  keys.sort(key = aSortKey)
  return keys

 def get_entry(self, aKey):
  return self._configitems.get(aKey,None)

 def get_select_entries(self, aKeyList):
  entries = []
  for key in aKeyList:
   entries.append(self._configitems.get(key))
  return entries

 def add_entry(self, aKey, aEntry, aWriteJSON = False):
  self._configitems[aKey] = aEntry
  if aWriteConf:
   if len(self._configitems) == 1:
    self.load_json()
   self.save_json()

#
# Database Class
#
class DB(object):

 def __init__(self):
  self._conn = None
  self._curs = None
  self._res  = 0

 def connect(self):
  import sdcp.SettingsContainer as SC
  import pymysql
  from pymysql.cursors import DictCursor
  self._conn = pymysql.connect(host='localhost', port=3306, user=SC.sdcp_dbuser, passwd=SC.sdcp_dbpass, db=SC.sdcp_db, cursorclass=DictCursor)
  self._curs = self._conn.cursor()

 #
 # Insert and Update and Select
 # 
 def do(self,aStr):
  self._res = self._curs.execute(aStr)
  return self._res

 def commit(self):
  self._conn.commit()

 def get_row(self):
  return self._curs.fetchone()

 def get_all_rows(self):
  return [] if self._res == 0 else self._curs.fetchmany(self._res)

 def get_cursor(self):
  return self._curs

 def close(self):
  self._curs.close()
  self._conn.close()
 
################################# Generics ####################################

_sys_debug = False

def sys_set_debug(astate):
 global _sys_debug
 _sys_debug = astate

def sys_get_host(ahost):
 from socket import gethostbyname
 try:
  return gethostbyname(ahost)
 except:
  return None

def sys_is_ip(addr):
 try:
  inet_aton(addr)
  return True
 except:
  return False

def sys_ip2int(addr):
 from struct import unpack
 from socket import inet_aton
 return unpack("!I", inet_aton(addr))[0]
 
def sys_int2ip(addr):
 from struct import pack
 from socket import inet_ntoa
 return inet_ntoa(pack("!I", addr))

def sys_ips2range(addr1,addr2):
 from struct import pack, unpack
 from socket import inet_ntoa, inet_aton
 return map(lambda addr: inet_ntoa(pack("!I", addr)), range(unpack("!I", inet_aton(addr1))[0], unpack("!I", inet_aton(addr2))[0] + 1))

def sys_ip2ptr(addr):
 octets = addr.split('.')
 octets.reverse()
 return ".".join(octets) + ".in-addr.arpa"

def sys_str2hex(arg):
 try:
  return '0x{0:02x}'.format(int(arg))
 except:
  return '0x00'    

def ping_os(ip):
 from os import system
 return system("ping -c 1 -w 1 " + ip + " > /dev/null 2>&1") == 0

def sys_get_results(test):
 return "success" if test else "failure"

def sys_log_msg(amsg):
 import sdcp.SettingsContainer as SC
 from time import localtime, strftime
 if _sys_debug: print "Log: " + amsg
 with open(SC.sdcp_logformat, 'a') as f:
  f.write(unicode("{} : {}\n".format(strftime('%Y-%m-%d %H:%M:%S', localtime()), amsg)))

#
# Lightweight argument parser, returns a dictionary with found arguments - { arg : value }
# Requires - or -- before any argument
#
def simple_arg_parser(args):
 # args should really be the argv
 argdict = {}
 currkey = None
 for arg in args:
  if arg.startswith('-'):
   if currkey:
    argdict[currkey] = True
   currkey = arg.lstrip('-')
  else:
   if currkey:
    argdict[currkey] = arg
    currkey = None
 if currkey:
  argdict[currkey] = True
 return argdict


def sys_write_pidfile(pidfname):
 pidfile = open(pidfname,'w')
 pidfile.write(str(getpid()))
 pidfile.close()

def sys_read_pidfile(pidfname):
 pid = -1
 from os import path as ospath
 if ospath.isfile(pidfname):
  pidfile = open(pidfname)
  pid = pidfile.readline().strip('\n')
  pidfile.close()
 return int(pid)

def sys_release_pidfile(pidfname):
 from os import path as ospath
 if ospath.isfile(pidfname):
  from os import remove
  remove(pidfname)

def sys_lock_pidfile(pidfname, sleeptime):
 from time import sleep
 from os import path as ospath
 while ospath.isfile(pidfname):
  sleep(sleeptime)
 sysWritePidFile(pidfname) 

def sys_file_replace(afile,old,new):
 if afile == "" or new == "" or old == "":
  return False

 filedata = None
 with open(afile, 'r') as f:
  filedata = f.read()

 filedata = filedata.replace(old,new)

 with open(afile, 'w') as f:
  f.write(filedata)
 return True
