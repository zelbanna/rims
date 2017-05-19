"""Module docstring.

Generic Device

"""
__author__ = "Zacharias El Banna"
__version__ = "10.5GA"
__status__ = "Production"

def is_ip(addr):
 from socket import inet_aton
 try:
  inet_aton(addr)
  return True
 except:
  return False

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
  if is_ip(ahost):
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
  from os import system
  return system("ping -c 1 -w 1 " + self._ip + " > /dev/null 2>&1") == 0

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

