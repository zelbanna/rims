"""Authentication API module. This module provides multi-service authentication initiation, relying on authentication services and the token database"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

#
#
def sync(aCTX, aArgs):
 """ Function sync authentication servers vs the token database

 Args:

 Output:
 """
 ret = {}
 servers = [{'service':v['service'],'node':v['node']} for v in aCTX.services.values() if v['type'] == 'AUTHENTICATION']
 with aCTX.db as db:
  db.do("SELECT id,alias FROM users WHERE id IN (%s)"%','.join([str(v['id']) for v in aCTX.tokens.values()]))
  alias = {x['id']:x['alias'] for x in db.get_rows()}
 users = [{'ip':v['ip'],'token':k,'alias':alias[v['id']]} for k,v in aCTX.tokens.items()]
 for infra in servers:
  aCTX.node_function(infra['node'],"services.%s"%infra['service'],'sync')(aArgs = users)
 return {'infra':servers, 'user':users}

#
#
def authenticate(aCTX, aArgs):
 """ Function authenticates a single user

 Args:
  - alias
  - ip
  - token

 Output:
  - status
 """
 ret = {'status':'OK'}
 auth = {'alias':aArgs['alias'], 'ip': aArgs['ip'], 'token': aArgs['token']}
 servers = [{'service':v['service'],'node':v['node']} for v in aCTX.services.values() if v['type'] == 'AUTHENTICATION']
 for infra in servers:
  res = aCTX.node_function(infra['node'],"services.%s"%infra['service'],'authenticate')(aArgs = auth)
  if res['status'] != 'OK':
   ret['status'] = 'NOT_OK'
   ret['info'] = res.get('info','node_function_error')
 return ret

#
#
def invalidate(aCTX, aArgs):
 """ Function invalidates a single user

 Args:
  - alias
  - ip
  - token

 Output:
  - status
 """
 ret = {'status':'OK'}
 auth = {'alias':aArgs['alias'], 'ip': aArgs['ip'], 'token': aArgs['token']}
 servers = [{'service':v['service'],'node':v['node']} for v in aCTX.services.values() if v['type'] == 'AUTHENTICATION']
 for infra in servers:
  res = aCTX.node_function(infra['node'],"services.%s"%infra['service'],'invalidate')(aArgs = auth)
  if res['status'] != 'OK':
   ret['status'] = 'NOT_OK'
   ret['info'] = res.get('info','node_function_error')
 return ret
