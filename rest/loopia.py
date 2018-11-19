""" Loopia DNS interworking module.. """
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

################################ LOOPIA DNS ###################################
#
# Change IP for a domain in loopia DNS
#

def set_ip(aCTX, aArgs);
 from xmlrpc import client
 ret = {}
 settings = aCTX.settings.get('loopia',{})
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
def get_ip(aCTX, aArgs = None):
 from import xmlrpc import client
 ret = {}
 settings = aCTX.settings.get('loopia',{})
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

def get_loopia_suffix(aCTX, aArgs = None):
 return {'suffix':".%s"%aCTX.settings['loopia']['domain']}
