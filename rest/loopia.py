""" Loopia DNS interworking module.. """
__author__ = "Zacharias El Banna"                     
__version__ = "5.4"
__status__ = "Production"

################################ LOOPIA DNS ###################################
#
# Change IP for a domain in loopia DNS
#

def set_ip(aDict, aCTX);
 ret = {}
 from xmlrpc import client
 with DB() as db:
  db.do("SELECT parameter,value FROM settings WHERE node = 'master' AND section = 'loopia'")
  settings = {s['parameter']:s['value'] for s in db.get_rows()}
 try:
  client = xmlrpc.client.ServerProxy(uri = settings['rpc_server'], encoding = 'utf-8')
  data = client.getZoneRecords(settings['username'], settings['password'], settings['domain'], aDict['subdomain'])[0]
  oldip = data['rdata']
  data['rdata'] = aDict['newip']
  ret['status'] = client.updateZoneRecord(settings['username'], settings['password'], settings['domain'], aDict['subdomain'], data)[0]
 except Exception as exmlrpc:
  ret['error']  = str(exmlrpc)
  ret['result'] = 'NOT_OK'
 else:
  ret['result'] = 'OK' 
 return ret

#
# Get Loopia settings for subdomain
#
def get_ip(aDict, aCTX):
 from import xmlrpc import client
 ret = {}
 with DB() as db:
  db.do("SELECT parameter,value FROM settings WHERE node = 'master' AND section = 'loopia'")
  settings = {s['parameter']:s['value'] for s in db.get_rows()}
 try:
  client = xmlrpc.client.ServerProxy(uri = settings['rpc_server'], encoding = 'utf-8')
  data = client.getZoneRecords(settings['username'], settings['password'], settings['domain'], aDict['subdomain'])[0]
 except Exception as exmlrpc:
  ret['error'] = str(exmlrpc)
  ret['result'] = 'NOT_OK'
 else:
  ret['info'] =  data['rdata']
  ret['result'] = 'OK' 
 return ret

def get_loopia_suffix(aDict, aCTX):
 with DB() as db:
  db.do("SELECT parameter,value FROM settings WHERE node = 'master' AND section = 'loopia'")
  settings = {s['parameter']:s['value'] for s in db.get_rows()}
 return {'suffix':".%s"%settings['domain']}

#
# Return external IP from opendns
#
def opendns_my_ip(aDict, aCTX):
 from .dns import resolver
 from socket import gethostbyname
 ret = {}
 try:
  opendns = resolver.Resolver()
  opendns.nameservers = [gethostbyname('resolver1.opendns.com')]
  myiplookup = opendns.query("myip.opendns.com",'A').response.answer[0]
 except Exception as exresolve:
  ret['error'] = str(exresolve)
  ret['result'] = 'NOT_OK'
 else:
  ret['address'] = str(myiplookup).split()[4]
  ret['result'] = 'OK' 
 return ret
