"""Module docstring.

 DNS interworking module

"""
__author__ = "Zacharias El Banna"                     
__version__ = "4.0GA"
__status__ = "Production"
from zdcp.core.common import DB, log

################################ LOOPIA DNS ###################################
#
# Change IP for a domain in loopia DNS
#

def set_loopia_ip(subdomain, newip):
 import xmlrpclib
 with DB() as db:
  db.do("SELECT parameter,value FROM settings WHERE node = 'master' AND section = 'loopia'")
  settings = {s['parameter']:s['value'] for s in db.get_rows()}
 try:
  client = xmlrpclib.ServerProxy(uri = settings['rpc_server'], encoding = 'utf-8')
  data = client.getZoneRecords(settings['username'], settings['password'], settings['domain'], subdomain)[0]
  oldip = data['rdata']
  data['rdata'] = newip
  status = client.updateZoneRecord(settings['username'], settings['password'], settings['domain'], subdomain, data)[0]
 except Exception as exmlrpc:
  log("System Error - Loopia set: " + str(exmlrpc))
  return False
 return True

#
# Get Loopia settings for subdomain
#
def get_loopia_ip(subdomain):
 import xmlrpclib
 with DB() as db:
  db.do("SELECT parameter,value FROM settings WHERE node = 'master' AND section = 'loopia'")
  settings = {s['parameter']:s['value'] for s in db.get_rows()}
 try:
  client = xmlrpclib.ServerProxy(uri = settings['rpc_server'], encoding = 'utf-8')
  data = client.getZoneRecords(settings['username'], settings['password'], settings['domain'], subdomain)[0]
  return data['rdata']
 except Exception as exmlrpc:
  log("System Error - Loopia get: " + str(exmlrpc))
  return False

def get_loopia_suffix():
 with DB() as db:
  db.do("SELECT parameter,value FROM settings WHERE node = 'master' AND section = 'loopia'")
  settings = {s['parameter']:s['value'] for s in db.get_rows()}
 return "." + settings['domain']

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
 
