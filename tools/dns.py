"""Module docstring.

 DNS interworking module

"""
__author__ = "Zacharias El Banna"                     
__version__ = "18.03.14GA"
__status__ = "Production"
from ..core.logger import log

################################ LOOPIA DNS ###################################
#
# Change IP for a domain in loopia DNS
#

def set_loopia_ip(subdomain, newip):
 from .. import SettingsContainer as SC
 import xmlrpclib
 try:
  client = xmlrpclib.ServerProxy(uri = SC.loopia['rpc_server'], encoding = 'utf-8')
  data = client.getZoneRecords(SC.loopia['username'], SC.loopia['password'], SC.loopia['domain'], subdomain)[0]
  oldip = data['rdata']
  data['rdata'] = newip
  status = client.updateZoneRecord(SC.loopia['username'], SC.loopia['password'], SC.loopia['domain'], subdomain, data)[0]
 except Exception as exmlrpc:
  log("System Error - Loopia set: " + str(exmlrpc))
  return False
 return True

#
# Get Loopia settings for subdomain
#
def get_loopia_ip(subdomain):
 from .. import SettingsContainer as SC
 import xmlrpclib
 try:
  client = xmlrpclib.ServerProxy(uri = SC.loopia['rpc_server'], encoding = 'utf-8')
  data = client.getZoneRecords(SC.loopia['username'], SC.loopia['password'], SC.loopia['domain'], subdomain)[0]
  return data['rdata']
 except Exception as exmlrpc:
  log("System Error - Loopia get: " + str(exmlrpc))
  return False

def get_loopia_suffix():
 from .. import SettingsContainer as SC
 return "." + SC.loopia['domain']

################################# OpenDNS ######################################
#
# Return external IP from opendns
#
def opendns_my_ip():
 from dns import resolver
 from socket import gethostbyname
 try:
  opendns = resolver.Resolver()
  opendns.nameservers = [gethostbyname('resolver1.opendns.com')]
  myiplookup = opendns.query("myip.opendns.com",'A').response.answer[0]
  return str(myiplookup).split()[4]
 except Exception as exresolve:
  log("OpenDNS Error - Resolve: " + str(exresolve))
  return False
 
############################### PDNS SYSTEM FUNCTIONS ##################################
#

def pdns_get():
 from subprocess import check_output
 recursor = check_output(["sudo","/bin/grep", "^recursor","/etc/powerdns/pdns.conf"])
 return recursor.split('=')[1].split('#')[0].strip()

#
# All-in-one, runs check, verify and (if needed) set and reload pdns service
# - returns True if was in sync and False if modified
# 
def pdns_sync(dnslist):
 from ..core.extras import file_replace
 pdns = pdns_get()
 if not pdns in dnslist:
  from subprocess import check_call
  from time import sleep
  log("System Info - updating recursor to " + dnslist[0])
  file_replace('/etc/powerdns/pdns.conf', pdns, dnslist[0])
  try:
   check_call(["/bin/systemctl","restart","pdns"])
   sleep(1)
  except Exception as svcerr:
   log("System Error - Reloading PowerDNS: " + str(svcerr))
  return False
 return True  
