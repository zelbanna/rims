"""
DNS API module. This module is a REST wrapper for interfaces to a particular DNS server type module.

This API will do all interaction with RIMS database and wrap actual service calls and data.

"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

################################ Domains ##################################
#
#
def domain_list(aCTX, aArgs):
 """Function docstring for domain_list.

 Args:
  - filter (optional)
  - sync (optional)

 Output:
  - filter:forward/reverse
 """
 ret = {}
 with aCTX.db as db:
  if aArgs.get('sync',False):
   org = {}
   for server in [{'id':k,'service':v['service'],'node':v['node']} for k,v in aCTX.services.items() if v['type'] == 'DNS']:
    org[server['id']] = aCTX.node_function(server['node'],server['service'],'domain_list')(aArgs = {})
   ret.update({'result':{'added':[],'deleted':[],'type_fix':0}})
   db.do("SELECT domains.*, CONCAT(server_id,'_',foreign_id) AS srv_id FROM domains")
   cache = db.get_dict('srv_id')
   for srv,info in org.items():
    for dom in info['data']:
     tmp = cache.pop("%s_%s"%(srv,dom['id']),None)
     if not tmp:
      ret['result']['added'].append(dom)
      # Add forward here
      db.insert_dict('domains',{'name':dom['name'],'server_id':srv,'foreign_id':dom['id'],'type':'reverse' if 'arpa' in dom['name'] else 'forward', 'endpoint':info['endpoint']},"ON DUPLICATE KEY UPDATE name = '%s', endpoint = '%s'"%(dom['name'],info['endpoint']))
     else:
      ret['result']['type_fix'] += db.do("UPDATE domains SET type = '%s', endpoint = '%s' WHERE id = %s"%('reverse' if 'arpa' in dom['name'] else 'forward',info['endpoint'],tmp['id']))
   for id,dom in cache.items():
    dom.pop('srv_id',None)
    ret['result']['deleted'].append(dom)
    db.do("DELETE FROM domains WHERE id = '%s'"%dom['id'])
   # Sync recursors as well
   # INTERNAL from rims.api.dns import sync
   sync(aCTX, aArgs = {})
  ret['count']   = db.do("SELECT domains.id, domains.name, st.service FROM domains LEFT JOIN servers ON domains.server_id = servers.id LEFT JOIN service_types AS st ON servers.type_id = st.id WHERE %s ORDER BY name"%("TRUE" if not 'filter' in aArgs else "domains.type = '%s'"%aArgs['filter']))
  ret['data'] = db.get_rows()
 return ret

#
#
def domain_info(aCTX, aArgs):
 """Function docstring for domain_info TBD

 Args:
  - id (required)
  - type (required)
  - master (required)
  - name (required)
  - server_id (optional)

 Output:
 """
 ret = {}
 id = aArgs['id']
 if id  == 'new' and not (aArgs.get('op') == 'update'):
  ret['servers'] = [{'id':k,'service':v['service'],'node':v['node']} for k,v in aCTX.services.items() if v['type'] == 'DNS']
  ret['data'] = {'id':'new','name':'new-name','master':'ip-of-master','type':'Master', 'serial':0 }
 else:
  with aCTX.db as db:
   if id == 'new':
    infra = (db.do("SELECT servers.id, 'new' AS foreign_id, st.service, node FROM servers LEFT JOIN service_types AS st ON servers.type_id = st.id WHERE servers.id = %s"%aArgs.pop('server_id','0')) > 0)
   else:
    infra = (db.do("SELECT servers.id,  foreign_id, st.service, node FROM servers LEFT JOIN service_types AS st ON servers.type_id = st.id LEFT JOIN domains ON domains.server_id = servers.id WHERE domains.id = %s"%id) > 0)
   if infra:
    ret['infra'] = db.get_row()
    aArgs['id']  = ret['infra']['foreign_id']
    ret.update(aCTX.node_function(ret['infra']['node'],ret['infra']['service'],'domain_info')(aArgs = aArgs))
    if ret.get('insert'):
     ret['cache'] = (db.insert_dict('domains',{'name':aArgs['name'],'server_id':ret['infra']['id'],'foreign_id':ret['data']['id'],'type':'reverse' if 'arpa' in aArgs['name'] else 'forward', 'endpoint':ret['endpoint']}) > 0)
     ret['infra']['foreign_id'] = ret['data']['id']
     ret['data']['id'] = db.get_last_id()
    elif ret.get('data'):
     ret['infra']['foreign_id'] = ret['data']['id']
     ret['data']['id'] = id
    else:
     ret['status'] = 'NOT_OK'
 return ret

#
#
def domain_delete(aCTX, aArgs):
 """Function domain_delete deletes a domain from local cache and remote DNS server. All records will be transferred to no domain.

 Args:
  - id (required)

 Output:
 """
 id = int(aArgs['id'])
 with aCTX.db as db:
  db.do("SELECT servers.id, foreign_id, domains.type, st.service, node FROM servers LEFT JOIN service_types AS st ON servers.type_id = st.id LEFT JOIN domains ON domains.server_id = servers.id WHERE domains.id = %i"%id)
  infra = db.get_row()
  ret = aCTX.node_function(infra['node'],infra['service'],'domain_delete')(aArgs = {'id':infra['foreign_id']})
  ret['local'] = db.do("UPDATE ipam_addresses SET a_domain_id = NULL WHERE a_domain_id = %i"%id)
  ret['networks'] = db.do("UPDATE ipam_networks SET reverse_zone_id = NULL WHERE reverse_zone_id = %i"%id)
  ret['cache'] = (db.do("DELETE FROM domains WHERE id = %i AND server_id = %s"%(id,infra['id'])) > 0) if ret['deleted'] else False
 return ret

#
#
def domain_ptr_list(aCTX, aArgs):
 """ Function returns matching PTR domain id's and extra server info for a prefix

 Args:
  - prefix

 Output:
  - List of id,servers and names which matches the prefix
 """
 def GL_ip2arpa(addr):
  octets = addr.split('.')[:3]
  octets.reverse()
  octets.append("in-addr.arpa")
  return ".".join(octets)
 with aCTX.db as db:
  db.do("SELECT domains.id, name, CONCAT(st.service,'@',node) AS server FROM domains LEFT JOIN servers ON domains.server_id = servers.id LEFT JOIN service_types AS st ON servers.type_id = st.id WHERE domains.name = '%s'"%(GL_ip2arpa(aArgs['prefix'])))
  domains = db.get_rows()
 return domains

#
#
def domain_forwarders(aCTX, aArgs):
 """ Function returns information for forwarders / recursors

 Args:

 Output:
  data - list of forwarding entries with the endpoint handling them
 """
 ret = {'status':'OK'}
 with aCTX.db as db:
  ret['count'] = db.do("SELECT domains.* FROM domains LEFT JOIN servers ON domains.server_id = servers.id LEFT JOIN service_types AS st ON servers.type_id = st.id WHERE domains.type = 'forward' AND st.service <> 'nodns'")
  ret['data'] = db.get_rows()
 return ret

######################################## Records ####################################
#
#
def record_list(aCTX, aArgs):
 """Function docstring for record_list TBD

 Args:
  - type (optional)
  - domain_id (required), <B>use internal/cached one</B>

 Output:
  - data
 """
 if aArgs.get('domain_id') is not None:
  with aCTX.db as db:
   db.do("SELECT foreign_id, st.service, node FROM servers LEFT JOIN service_types AS st ON servers.type_id = st.id LEFT JOIN domains ON domains.server_id = servers.id WHERE domains.id = %s"%aArgs['domain_id'])
   infra = db.get_row()
   aArgs['domain_id'] = infra['foreign_id']
 else:
  # Strictly internal use - this one fetch all records for consistency check
  infra = aCTX.services.get(aArgs['server_id'])
  aArgs.pop('server_id',None)
 ret = aCTX.node_function(infra['node'],infra['service'],'record_list')(aArgs = aArgs)
 ret['domain_id'] = aArgs.get('domain_id',0)
 return ret

#
#
def record_info(aCTX, aArgs):
 """Function docstring for record_info TBD

 Args:
  - name (required)
  - domain_id (required)
  - type (required)
  - op (required) 'new'/'info'/'insert'/'update'
  - content (optional)

 Output:
 """
 ret = {}
 if aArgs['domain_id'] is None or len(aArgs['name']) == 0 or len(aArgs['type']) == 0:
  ret = {'status':'NOT_OK', 'data':None, 'info':'Not enough correct parameters (domain,name,type)'}
 elif aArgs['op'] == 'new':
  ret = {'status':'OK', 'data':{'domain_id':aArgs['domain_id'],'name':'key','content':'value','type':'type-of-record','ttl':'3600'}}
 else:
  domain_id = aArgs['domain_id']
  with aCTX.db as db:
   db.do("SELECT foreign_id, st.service, node FROM servers LEFT JOIN service_types AS st ON servers.type_id = st.id LEFT JOIN domains ON domains.server_id = servers.id WHERE domains.id = %s"%domain_id)
   infra = db.get_row()
   aArgs['domain_id'] = infra['foreign_id']
  ret = aCTX.node_function(infra['node'],infra['service'],'record_info')(aArgs = aArgs)
  if ret.get('data'):
   ret['data']['domain_id'] = domain_id
  ret['status'] = ret.get('status','OK')
 return ret

#
#
def record_delete(aCTX, aArgs):
 """Function docstring for record_delete TBD

 Args:
  - name (required)
  - domain_id (required)
  - type (optional)

 Output:
 """
 with aCTX.db as db:
  db.do("SELECT foreign_id, st.service, node FROM servers LEFT JOIN service_types AS st ON servers.type_id = st.id LEFT JOIN domains ON domains.server_id = servers.id WHERE domains.id = %s"%aArgs['domain_id'])
  infra = db.get_row()
 aArgs['domain_id'] = infra['foreign_id']
 return aCTX.node_function(infra['node'],infra['service'],'record_delete')(aArgs = aArgs)

###################################### Tools ####################################
#
#
def status(aCTX, aArgs):
 """Function docstring for status TBD

 Args:
  - count (optional)

 Output:
  - top
  - who
 """
 ret = {'top':{},'who':{}}
 args = {'count':aArgs.get('count',20)}
 for infra in [{'service':v['service'],'node':v['node']} for v in aCTX.services.values() if v['type'] == 'DNS']:
  res = aCTX.node_function(infra['node'],infra['service'],'status')(aArgs = args)
  ret['top']["%(node)s_%(service)s"%infra] = res['top']
  ret['who']["%(node)s_%(service)s"%infra] = res['who']
 return ret

#
#
def sync(aCTX, aArgs):
 """ Function synchronizes recursors and with database/forwarders to point to the right DNS servers

 Args:

 Output:
 """
 ret = {'added':[],'removed':[],'errors':[]}
 # INTERNAL from rims.api.dns import domain_forwarders
 domains = domain_forwarders(aCTX,{})['data']
 for infra in [{'service':v['service'],'node':v['node']} for v in aCTX.services.values() if v['type'] == 'RECURSOR']:
  res = aCTX.node_function(infra['node'],infra['service'],'sync')(aArgs = {'domains':domains})
  if res['status'] == 'OK':
   ret['added'].extend(res['added'])
   ret['removed'].extend(res['removed'])
  else:
   ret['errors'].append(("%s@%s"%(infra['node'],infra['service']),res['info']))
  ret['status'] = 'NOT_OK' if ret['errors'] else 'OK'
 aCTX.log("DNS <=> Recursors synchronized: %s"%ret['status'])
 return ret
