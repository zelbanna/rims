"""Module docstring.

Generic Library

"""
__author__ = "Zacharias El Banna"
__version__ = "10.5GA"
__status__ = "Production"

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
  self._devid = None
  if sys_is_ip(ahost):
   self._ip = ahost
   try:
    self._fqdn = getfqdn(ahost)
    self._hostname = self._fqdn.partition('.')[0]
    self._domain   = self._fqdn.partition('.')[2]
   except:
    self._fqdn = ahost
    self._hostname = ahost
    self._domain = adomain
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
  return ping_os(self._ip)

 def get_type(self):
  return self._type

 def log_msg(self, aMsg, aPrint = False):
  from time import localtime, strftime
  output = unicode("{} : {}".format(strftime('%Y-%m-%d %H:%M:%S', localtime()), aMsg))
  if aPrint:
   print output
  with open(self._logfile, 'a') as f:
   f.write(output + "\n")

 def print_conf(self,argdict):
  print "No config for device"

############################################ Database ######################################
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
  from pymysql import connect
  from pymysql.cursors import DictCursor
  self._conn = connect(host='localhost', port=3306, user=SC.sdcp_dbuser, passwd=SC.sdcp_dbpass, db=SC.sdcp_db, cursorclass=DictCursor)
  self._curs = self._conn.cursor()

 def connect_details(self, aHost, aUser, aPass, aDB):
  from pymysql import connect
  from pymysql.cursors import DictCursor
  self._conn = connect(host=aHost, port=3306, user=aUser, passwd=aPass, db=aDB, cursorclass=DictCursor)
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

 def get_all_dict(self, aTarget):
  return {} if self._res == 0 else dict(map(lambda x: (x[aTarget],x),self._curs.fetchmany(self._res)))

 def get_cursor(self):
  return self._curs

 def close(self):
  self._curs.close()
  self._conn.close()

################################ RPC ###########################################

def rpc_call(aurl,op,args):
  from json import loads, dumps
  from urllib import urlopen
  arg = dumps(args)
  lnk = aurl + "rest.cgi?rpc={}&args={}".format(op,arg)
  try:
   sys_log_msg(lnk)
   sock = urlopen(lnk)
   res  = sock.read()
   sock.close()
   return loads(res)
  except Exception as err:
   return { 'err':str(err) }
 
################################# Generics ####################################

def sys_get_host(ahost):
 from socket import gethostbyname
 try:
  return gethostbyname(ahost)
 except:
  return None

def sys_is_ip(addr):
 from socket import inet_aton
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

def sys_int2mac(aInt):
 return ':'.join(s.encode('hex') for s in str(hex(aInt))[2:].zfill(12).decode('hex')).upper()

def sys_is_mac(aMAC):           
 try:
  aMAC = aMAC.replace(":","")
  return len(aMAC) == 12 and int(aMAC,16)
 except:         
  return False

def ping_os(ip):
 from os import system
 return system("ping -c 1 -w 1 " + ip + " > /dev/null 2>&1") == 0

def sys_log_msg(amsg):
 import sdcp.SettingsContainer as SC
 from time import localtime, strftime
 with open(SC.sdcp_logformat, 'a') as f:
  f.write(unicode("{} : {}\n".format(strftime('%Y-%m-%d %H:%M:%S', localtime()), amsg)))
