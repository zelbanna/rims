"""Module docstring.

 DNS interworking module

"""
__author__ = "Zacharias El Banna"                     
__version__ = "18.05.31GA"
__status__ = "Production"
from zdcp.core.logger import log

################################ LOOPIA DNS ###################################
#
# Change IP for a domain in loopia DNS
#

def set_loopia_ip(subdomain, newip):
 from zdcp.SettingsContainer import SC
 import xmlrpclib
 try:
  client = xmlrpclib.ServerProxy(uri = SC['loopia']['rpc_server'], encoding = 'utf-8')
  data = client.getZoneRecords(SC['loopia']['username'], SC['loopia']['password'], SC['loopia']['domain'], subdomain)[0]
  oldip = data['rdata']
  data['rdata'] = newip
  status = client.updateZoneRecord(SC['loopia']['username'], SC['loopia']['password'], SC['loopia']['domain'], subdomain, data)[0]
 except Exception as exmlrpc:
  log("System Error - Loopia set: " + str(exmlrpc))
  return False
 return True

#
# Get Loopia settings for subdomain
#
def get_loopia_ip(subdomain):
 from zdcp.SettingsContainer import SC
 import xmlrpclib
 try:
  client = xmlrpclib.ServerProxy(uri = SC['loopia']['rpc_server'], encoding = 'utf-8')
  data = client.getZoneRecords(SC['loopia']['username'], SC['loopia']['password'], SC['loopia']['domain'], subdomain)[0]
  return data['rdata']
 except Exception as exmlrpc:
  log("System Error - Loopia get: " + str(exmlrpc))
  return False

def get_loopia_suffix():
 from zdcp.SettingsContainer import SC
 return "." + SC['loopia']['domain']

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
 
