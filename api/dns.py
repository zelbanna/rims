"""DNS API module.

- This module is a REST wrapper for interfaces to a particular DNS server type module.
- The API will do all interaction with RIMS database and wrap actual service calls and data.
"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

################################ Domains ##################################
#
#
def domain_list(aRT, aArgs):
 """Function docstring for domain_list.

 Args:
  - filter (optional)
  - sync (optional)

 Output:
  - filter:forward/reverse
 """
 ret = {}
 with aRT.db as db:
  if aArgs.get('sync',False):
   # INTERNAL from rims.api.dns import sync_recursor, sync_nameserver
   ret['ns'] = sync_nameserver(aRT, aArgs = {})
   ret['rec'] = sync_recursor(aRT, aArgs = {})
  ret['count'] = db.query("SELECT domains.id, domains.name, st.service FROM domains LEFT JOIN servers ON domains.server_id = servers.id LEFT JOIN service_types AS st ON servers.type_id = st.id WHERE %s ORDER BY name"%("TRUE" if 'filter' not in aArgs else "domains.type = '%s'"%aArgs['filter']))
  ret['data'] = db.get_rows()
 return ret

#
#
def domain_info(aRT, aArgs):
 """Function docstring for domain_info TBD

 Args:
  - id (required)
  - type (required)
  - master (required)
  - name (required)
  - server_id (optional)
  - op (optional)

 Output:
 """
 ret = {}
 id = aArgs['id']
 if id  == 'new' and aArgs.get('op') != 'update':
  ret['servers'] = [{'id':k,'service':v['service'],'node':v['node']} for k,v in aRT.services.items() if v['type'] == 'NAMESERVER']
  ret['data'] = {'id':'new','name':'new-name','master':'ip-of-master','type':'Master', 'serial':0 }
 else:
  with aRT.db as db:
   if id == 'new':
    infra = bool(db.query("SELECT servers.id, 'new' AS foreign_id, st.service, node FROM servers LEFT JOIN service_types AS st ON servers.type_id = st.id WHERE servers.id = %s"%aArgs.pop('server_id','0')))
   else:
    infra = bool(db.query("SELECT servers.id,  foreign_id, st.service, node FROM servers LEFT JOIN service_types AS st ON servers.type_id = st.id LEFT JOIN domains ON domains.server_id = servers.id WHERE domains.id = %s"%id))
   if infra:
    ret['infra'] = db.get_row()
    aArgs['id']  = ret['infra']['foreign_id']
    ret.update(aRT.node_function(ret['infra']['node'],"services.%s"%ret['infra']['service'],'domain_info')(aArgs = aArgs))
    if ret.get('insert'):
     ret['cache'] = bool(db.insert_dict('domains',{'name':aArgs['name'],'server_id':ret['infra']['id'],'foreign_id':ret['data']['id'],'master':aArgs['master'],'type':'reverse' if 'arpa' in aArgs['name'] else 'forward', 'endpoint':ret['endpoint']}))
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
def domain_delete(aRT, aArgs):
 """Function domain_delete deletes a domain from local caching and remote nameserver. All records will have no domain

 Args:
  - id (required)

 Output:
 """
 id = int(aArgs['id'])
 with aRT.db as db:
  db.query("SELECT servers.id, foreign_id, domains.type, st.service, node FROM servers LEFT JOIN service_types AS st ON servers.type_id = st.id LEFT JOIN domains ON domains.server_id = servers.id WHERE domains.id = %i"%id)
  infra = db.get_row()
  ret = aRT.node_function(infra['node'],"services.%s"%infra['service'],'domain_delete')(aArgs = {'id':infra['foreign_id']})
  ret['cache'] = bool(db.execute("DELETE FROM domains WHERE id = %i AND server_id = %s"%(id,infra['id']))) if ret['deleted'] else False
 return ret

#
#
def domain_ptr_list(aRT, aArgs):
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
 with aRT.db as db:
  db.query("SELECT domains.id, name, CONCAT(st.service,'@',node) AS server FROM domains LEFT JOIN servers ON domains.server_id = servers.id LEFT JOIN service_types AS st ON servers.type_id = st.id WHERE domains.name = '%s'"%(GL_ip2arpa(aArgs['prefix'])))
  domains = db.get_rows()
 return domains

#
#
def domain_forwarders(aRT, aArgs):
 """ Function returns information for forwarders / recursors

 Args:

 Output:
  data - list of forwarding entries with the endpoint handling them
 """
 ret = {'status':'OK'}
 with aRT.db as db:
  ret['count'] = db.query("SELECT domains.name, domains.foreign_id, domains.endpoint FROM domains LEFT JOIN servers ON domains.server_id = servers.id LEFT JOIN service_types AS st ON servers.type_id = st.id WHERE domains.type = 'forward' AND st.service <> 'nodns'")
  ret['data'] = db.get_rows()
 return ret

######################################## Records ####################################
#
#
def record_list(aRT, aArgs):
 """Function docstring for record_list TBD

 Args:
  - type (optional)
  - domain_id (required), <B>use internal/cached one</B>

 Output:
  - data
 """
 if aArgs.get('domain_id') is not None:
  with aRT.db as db:
   db.query("SELECT foreign_id, st.service, node FROM servers LEFT JOIN service_types AS st ON servers.type_id = st.id LEFT JOIN domains ON domains.server_id = servers.id WHERE domains.id = %s"%aArgs['domain_id'])
   infra = db.get_row()
   aArgs['domain_id'] = infra['foreign_id']
 else:
  # Strictly internal use - this one fetch all records for consistency check
  infra = aRT.services.get(aArgs['server_id'])
  aArgs.pop('server_id',None)
 ret = aRT.node_function(infra['node'],"services.%s"%infra['service'],'record_list')(aArgs = aArgs)
 ret['domain_id'] = aArgs.get('domain_id',0)
 return ret

#
#
def record_info(aRT, aArgs):
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
 if not (aArgs['domain_id'] and aArgs['name'] and aArgs['type']):
  ret = {'status':'NOT_OK', 'data':None, 'info':'Not enough correct parameters (domain,name,type)'}
 elif aArgs['op'] == 'new':
  ret = {'status':'OK', 'data':{'domain_id':aArgs['domain_id'],'name':'key','content':'value','type':'type-of-record','ttl':'3600'}}
 else:
  domain_id = aArgs['domain_id']
  with aRT.db as db:
   db.query("SELECT foreign_id, st.service, node FROM servers LEFT JOIN service_types AS st ON servers.type_id = st.id LEFT JOIN domains ON domains.server_id = servers.id WHERE domains.id = %s"%domain_id)
   infra = db.get_row()
   aArgs['domain_id'] = infra['foreign_id']
  ret = aRT.node_function(infra['node'],"services.%s"%infra['service'],'record_info')(aArgs = aArgs)
  if ret.get('data'):
   ret['data']['domain_id'] = domain_id
  ret['status'] = ret.get('status','OK')
 return ret

#
#
def record_delete(aRT, aArgs):
 """Function docstring for record_delete TBD

 Args:
  - name (required)
  - domain_id (required)
  - type (optional)

 Output:
 """
 with aRT.db as db:
  db.query("SELECT foreign_id, st.service, node FROM servers LEFT JOIN service_types AS st ON servers.type_id = st.id LEFT JOIN domains ON domains.server_id = servers.id WHERE domains.id = %s"%aArgs['domain_id'])
  infra = db.get_row()
 aArgs['domain_id'] = infra['foreign_id']
 return aRT.node_function(infra['node'],"services.%s"%infra['service'],'record_delete')(aArgs = aArgs)

###################################### Tools ####################################
#
#
def statistics(aRT, aArgs):
 """Function returns statistics from all recursors

 Args:
  - count (optional)

 Output:
  - queries
  - remotes
 """
 ret = {'queries':{},'remotes':{}}
 args = {'count':aArgs.get('count',20)}
 for infra in [{'service':v['service'],'node':v['node']} for v in aRT.services.values() if v['type'] == 'RECURSOR']:
  res = aRT.node_function(infra['node'],"services.%s"%infra['service'],'statistics')(aArgs = args)
  ret['queries']["%(node)s_%(service)s"%infra] = res['queries']
  ret['remotes']["%(node)s_%(service)s"%infra] = res['remotes']
 return ret

#
#
def sync_nameserver(aRT, aArgs):
 """ Function synchronizes nameservers with the local cached

 Args:

 Output:
 """
 ret = {'added':[],'removed':[],'fixed':0,'errors':[]}
 org = {}
 for infra in [{'id':k,'service':v['service'],'node':v['node']} for k,v in aRT.services.items() if v['type'] == 'NAMESERVER']:
  res = aRT.node_function(infra['node'],"services.%s"%infra['service'],'domain_list')(aArgs = {})
  if res['status'] == 'OK':
   org[infra['id']] = res
  else:
   ret['errors'].append(("%s@%s"%(infra['node'],infra['service']),res['info']))
 if ret['errors']:
  ret['status'] = 'NOT_OK'
  return ret
 else:
  ret['status'] = 'OK'

 with aRT.db as db:
  db.query("SELECT domains.*, CONCAT(server_id,'_',foreign_id) AS srv_id FROM domains")
  cache = db.get_dict('srv_id')
  for srv,info in org.items():
   for dom in info['data']:
    tmp = cache.pop("%s_%s"%(srv,dom['id']),None)
    if not tmp:
     ret['added'].append(dom)
     # Add forward here
     db.insert_dict('domains',{'name':dom['name'],'server_id':srv,'foreign_id':dom['id'],'type':'reverse' if 'arpa' in dom['name'] else 'forward', 'endpoint':info['endpoint']},"ON DUPLICATE KEY UPDATE name = '%s', endpoint = '%s'"%(dom['name'],info['endpoint']))
    else:
     ret['fixed'] += db.execute("UPDATE domains SET type = '%s', endpoint = '%s' WHERE id = %s"%('reverse' if 'arpa' in dom['name'] else 'forward',info['endpoint'],tmp['id']))
  for id,dom in cache.items():
   dom.pop('srv_id',None)
   ret['removed'].append(dom)
   db.execute("DELETE FROM domains WHERE id = '%s'"%dom['id'])
 return ret

#
#
def sync_recursor(aRT, aArgs):
 """ Function synchronizes recursors and with database/forwarders to point them to the correct nameserver

 Args:

 Output:
 """
 ret = {'added':[],'removed':[],'errors':[]}
 # INTERNAL from rims.api.dns import domain_forwarders
 domains = domain_forwarders(aRT,{})['data']
 for infra in [{'service':v['service'],'node':v['node']} for v in aRT.services.values() if v['type'] == 'RECURSOR']:
  res = aRT.node_function(infra['node'],"services.%s"%infra['service'],'sync')(aArgs = {'domains':domains})
  if res['status'] == 'OK':
   ret['added'].extend(res['added'])
   ret['removed'].extend(res['removed'])
  else:
   ret['errors'].append(("%s@%s"%(infra['node'],infra['service']),res['info']))
  ret['status'] = 'NOT_OK' if ret['errors'] else 'OK'
 return ret

#
def sync_data(aRT, aArgs):
 """ Function retrieves various data for synchronizing nameservers, data is retrieved in canonical format. Only return PTR records that fits a /24

 Args:
  - server_id (required). Server id
  - foreign_id (required). Foreign ID for domain to sync (i.e. local to server)

 Output:
  - data
  - status
 """
 ret = {}
 with aRT.db as db:
  if db.query("SELECT id,type FROM domains WHERE server_id = %(server_id)s AND foreign_id = '%(foreign_id)s'"%aArgs):
   ret['status'] = 'OK'
   domain = db.get_row()
   if domain['type'] == 'forward':
    db.query("SELECT CONCAT(ia.hostname,'.',domains.name,'.') AS name, INET6_NTOA(ia.ip) AS content, IF(IS_IPV4(INET6_NTOA(ine.network)),'A','AAAA') AS type FROM ipam_addresses AS ia LEFT JOIN ipam_networks AS ine ON ia.network_id = ine.id LEFT JOIN domains ON domains.id = ia.a_domain_id WHERE domains.id = %s ORDER BY domains.foreign_id"%domain['id'])
    ret['data'] = db.get_rows()
    db.query("SELECT CONCAT(devices.hostname,'.',domains.name,'.') AS name, INET6_NTOA(ia.ip) AS content, IF(IS_IPV4(INET6_NTOA(ine.network)),'A','AAAA') AS type FROM devices LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id LEFT JOIN ipam_networks AS ine ON ia.network_id = ine.id LEFT JOIN domains ON devices.a_domain_id = domains.id WHERE devices.a_domain_id = %s AND ia.id IS NOT NULL ORDER BY devices.a_domain_id"%domain['id'])
    ret['data'].extend(db.get_rows())
   else:
    from ipaddress import IPv4Address, IPv4Network
    ret['data'] = []
    db.query("SELECT INET6_NTOA(ip) AS ip, INET6_NTOA(ine.network) AS network, ine.mask, CONCAT(ia.hostname,'.',domains.name,'.') AS content FROM ipam_addresses AS ia RIGHT JOIN domains ON ia.a_domain_id = domains.id LEFT JOIN ipam_networks AS ine ON ia.network_id = ine.id AND IS_IPV4(INET6_NTOA(ine.network)) LEFT JOIN domains AS ia_dom ON ine.reverse_zone_id = ia_dom.id WHERE ine.reverse_zone_id = %s AND domains.name IS NOT NULL ORDER BY ine.reverse_zone_id"%domain['id'])
    for addr in db.get_rows():
     ip = IPv4Address(addr['ip'])
     if addr['mask'] >= 24 or ip in IPv4Network('%s/24'%addr['network']):
      ret['data'].append({'name':ip.reverse_pointer,'content':addr['content'],'type':'PTR'})
  else:
   ret['status'] = 'NOT_OK'
   ret['info'] = 'server/domain pair mismatch'
 return ret
