""" Loopia DNS interworking module.. """
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

################################ LOOPIA DNS ###################################
#
# Change IP for a domain in loopia DNS
#

def set_ip(aCTX, aArgs);
 ret = {}
 from xmlrpc import client
 with DB() as db:
  db.do("SELECT parameter,value FROM settings WHERE node = 'master' AND section = 'loopia'")
  settings = {s['parameter']:s['value'] for s in db.get_rows()}
 try:
  client = xmlrpc.client.ServerProxy(uri = settings['rpc_server'], encoding = 'utf-8')
  data = client.getZoneRecords(settings['username'], settings['password'], settings['domain'], aArgs['subdomain'])[0]
  oldip = data['rdata']
  data['rdata'] = aArgs['newip']
  ret['status'] = client.updateZoneRecord(settings['username'], settings['password'], settings['domain'], aArgs['subdomain'], data)[0]
 except Exception as exmlrpc:
  ret['error']  = repr(exmlrpc)
  ret['status'] = 'NOT_OK'
 else:
  ret['status'] = 'OK'
 return ret

#
# Get Loopia settings for subdomain
#
def get_ip(aCTX, aArgs):
 from import xmlrpc import client
 ret = {}
 with DB() as db:
  db.do("SELECT parameter,value FROM settings WHERE node = 'master' AND section = 'loopia'")
  settings = {s['parameter']:s['value'] for s in db.get_rows()}
 try:
  client = xmlrpc.client.ServerProxy(uri = settings['rpc_server'], encoding = 'utf-8')
  data = client.getZoneRecords(settings['username'], settings['password'], settings['domain'], aArgs['subdomain'])[0]
 except Exception as exmlrpc:
  ret['error']  = repr(exmlrpc)
  ret['status'] = 'NOT_OK'
 else:
  ret['info'] =  data['rdata']
  ret['status'] = 'OK'
 return ret

def get_loopia_suffix(aCTX, aArgs):
 with DB() as db:
  db.do("SELECT parameter,value FROM settings WHERE node = 'master' AND section = 'loopia'")
  settings = {s['parameter']:s['value'] for s in db.get_rows()}
 return {'suffix':".%s"%settings['domain']}
