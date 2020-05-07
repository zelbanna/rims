""" Loopia DNS interworking module..

Config section loopia:
 - username
 - password
 - rpc_server
 - domain

"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

################################ LOOPIA DNS ###################################
#
# Change IP for a domain in loopia DNS
#

def set_ip(aCTX, aArgs):
 from xmlrpc import client
 ret = {}
 try:
  client = xmlrpc.client.ServerProxy(uri = aCTX.config['loopia']['rpc_server'], encoding = 'utf-8')
  data = client.getZoneRecords(aCTX.config['loopia']['username'], aCTX.config['loopia']['password'], aCTX.config['loopia']['domain'], aArgs['subdomain'])[0]
  oldip = data['rdata']
  data['rdata'] = aArgs['newip']
  ret['status'] = client.updateZoneRecord(aCTX.config['loopia']['username'], aCTX.config['loopia']['password'], aCTX.config['loopia']['domain'], aArgs['subdomain'], data)[0]
 except Exception as exmlrpc:
  ret['error']  = repr(exmlrpc)
  ret['status'] = 'NOT_OK'
 else:
  ret['status'] = 'OK'
 return ret

#
# Get Loopia info for subdomain
#
def get_ip(aCTX, aArgs):
 from xmlrpc import client
 ret = {}
 try:
  client = xmlrpc.client.ServerProxy(uri = aCTX.config['loopia']['rpc_server'], encoding = 'utf-8')
  data = client.getZoneRecords(aCTX.config['loopia']['username'], aCTX.config['loopia']['password'], aCTX.config['loopia']['domain'], aArgs['subdomain'])[0]
 except Exception as exmlrpc:
  ret['status'] = 'NOT_OK'
  ret['info']  = repr(exmlrpc)
 else:
  ret['data'] =  data['rdata']
  ret['status'] = 'OK'
 return ret

#
#
def get_loopia_suffix(aCTX, aArgs):
 return {'suffix':".%s"%aCTX.config['loopia']['domain']}
