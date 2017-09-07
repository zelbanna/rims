"""Module docstring.

 DNS interworking module

"""
__author__ = "Zacharias El Banna"                     
__version__ = "17.6.1GA"
__status__ = "Production"
import sdcp.SettingsContainer as SC
import sdcp.core.GenLib as GL

################################ LOOPIA DNS ###################################
#
# Change IP for a domain in loopia DNS
#
loopia_domain_server_url = 'https://api.loopia.se/RPCSERV' 

def set_loopia_ip(subdomain, newip):
 import xmlrpclib
 try:
  client = xmlrpclib.ServerProxy(uri = loopia_domain_server_url, encoding = 'utf-8')
  data = client.getZoneRecords(SC.loopia_username, SC.loopia_password, SC.loopia_domain, subdomain)[0]
  oldip = data['rdata']
  data['rdata'] = newip
  status = client.updateZoneRecord(SC.loopia_username, SC.loopia_password, SC.loopia_domain, subdomain, data)[0]
 except Exception as exmlrpc:
  GL.log_msg("System Error - Loopia set: " + str(exmlrpc))
  return False
 return True

#
# Get Loopia settings for subdomain
#
def get_loopia_ip(subdomain):
 import xmlrpclib
 try:
  client = xmlrpclib.ServerProxy(uri = loopia_domain_server_url, encoding = 'utf-8')
  data = client.getZoneRecords(SC.loopia_username, SC.loopia_password, SC.loopia_domain, subdomain)[0]
  return data['rdata']
 except Exception as exmlrpc:
  GL.log_msg("System Error - Loopia get: " + str(exmlrpc))
  return False

def get_loopia_suffix():
 return "." + SC.loopia_domain

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
  GL.log_msg("OpenDNS Error - Resolve: " + str(exresolve))
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
 from sdcp.core.XtraLib import file_replace
 pdns = pdns_get()
 if not pdns in dnslist:
  from subprocess import check_call
  from time import sleep
  GL.log_msg("System Info - updating recursor to " + dnslist[0])
  file_replace('/etc/powerdns/pdns.conf', pdns, dnslist[0])
  try:
   check_call(["/bin/systemctl","restart","pdns"])
   sleep(1)
  except Exception as svcerr:
   GL.log_msg("System Error - Reloading PowerDNS: " + str(svcerr))
  return False
 return True  
