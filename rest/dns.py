"""DNS API module. This module is a REST wrapper for interfaces to a particular DNS server (device) type module.
Settings:
 - node
 - type

"""
__author__ = "Zacharias El Banna"
__version__ = "4.0GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

################################ Domains ##################################
#
#
def domain_list(aDict, aCTX):
 """Function docstring for domain_list.

 Args:
  - filter (optional)
  - dict (optional)
  - sync (optional)
  - exclude (optional)

 Output:
  - filter:forward/reverse
 """
 ret = {}
 with aCTX.db as db:
  if aDict.get('sync'):
   org = {}
   db.do("SELECT id, server, node FROM servers WHERE type = 'DNS'")
   servers = db.get_rows()
   for server in servers:
    org[server['id']] = aCTX.node_call(server['node'],server['server'],'domain_list')['domains']
   ret.update({'sync':{'added':[],'deleted':[],'type_fix':0}})
   db.do("SELECT domains.*, CONCAT(server_id,'_',foreign_id) AS srv_id FROM domains")
   cache = db.get_dict('srv_id')
   for srv,domains in org.iteritems():
    for dom in domains:
     tmp = cache.pop("%s_%s"%(srv,dom['id']),None)
     if not tmp:
      ret['sync']['added'].append(dom)
      # Add forward here
      db.insert_dict('domains',{'name':dom['name'],'server_id':srv,'foreign_id':dom['id'],'type':'reverse' if 'arpa' in dom['name'] else 'forward'},"ON DUPLICATE KEY UPDATE name = '%s'"%dom['name'])
     else:
      ret['sync']['type_fix'] += db.do("UPDATE domains SET type = '%s' WHERE id = %s"%('reverse' if 'arpa' in dom['name'] else 'forward',tmp['id']))
   for id,dom in cache.iteritems():
    dom.pop('srv_id',None)
    ret['sync']['deleted'].append(dom)
    db.do("DELETE FROM domains WHERE id = '%s'"%dom['id'])

  filter = []
  if aDict.get('filter'):
   filter.append("domains.type = '%s'"%aDict.get('filter'))
  if aDict.get('exclude'):
   db.do("SELECT server_id FROM domains WHERE id = '%s'"%(aDict.get('exclude')))
   filter.append('server_id = %s'%(db.get_val('server_id')))
   filter.append("domains.id <> '%s'"%aDict.get('exclude'))

  ret['count']   = db.do("SELECT domains.*, server FROM domains LEFT JOIN servers ON domains.server_id = servers.id WHERE %s ORDER BY name"%('TRUE' if len(filter) == 0 else " AND ".join(filter)))
  ret['domains'] = db.get_rows() if not aDict.get('dict') else db.get_dict(aDict.get('dict'))
 return ret

#
#
def domain_info(aDict, aCTX):
 """Function docstring for domain_info TBD

 Args:
  - id (required)
  - type (required)
  - master (required)
  - name (required)
  - server_id (optional)

 Output:
 """
 ret = {'id':aDict['id']}
 with aCTX.db as db:
  if aDict['id'] == 'new' and not (aDict.get('op') == 'update'):
   db.do("SELECT id, server, node FROM servers WHERE type = 'DNS'")
   ret['servers'] = db.get_rows()
   ret['data'] = {'id':'new','name':'new-name','master':'ip-of-master','type':'MASTER', 'notified_serial':0 }
  else:
   if aDict['id'] == 'new':
    db.do("SELECT id, 'new' AS foreign_id, server, node FROM servers WHERE id = %s"%aDict.pop('server_id','0'))
   else:
    db.do("SELECT servers.id, foreign_id, server, node FROM servers LEFT JOIN domains ON domains.server_id = servers.id WHERE domains.id = %s"%aDict['id'])
   ret['infra'] = db.get_row()
   aDict['id']   = ret['infra'].pop('foreign_id',None)
   ret.update(aCTX.node_call(ret['infra']['node'],ret['infra']['server'],'domain_info',aDict))
   if str(ret.get('insert',0)) == '1':
    ret['cache'] = db.insert_dict('domains',{'name':aDict['name'],'server_id':ret['infra']['id'],'foreign_id':ret['data']['id']})
    ret['id'] = db.get_last_id() 
 return ret

#
#
def domain_delete(aDict, aCTX):
 """Function domain_delete deletes a domain from local cache and remote DNS server. All records will be transferred to default (0) domain.

 Args:
  - id (required)

 Output:
 """
 ret = {}
 id = int(aDict['id'])
 with aCTX.db as db:
  db.do("SELECT foreign_id, server, node FROM servers LEFT JOIN domains ON domains.server_id = servers.id WHERE domains.id = %i"%id)
  infra = db.get_row()
  ret = aCTX.node_call(infra['node'],infra['server'],'domain_delete',{'id':infra['foreign_id']})
  ret['local'] = db.do("UPDATE devices SET a_dom_id = 0 WHERE a_dom_id = %i"%id)
  ret['cache'] = db.do("DELETE FROM domains WHERE id = %i"%id) if ret['domain'] else 0
 return ret

#
#
def domain_ptr_list(aDict, aCTX):
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
  db.do("SELECT domains.id, name, CONCAT(server,'@',node) AS server FROM domains LEFT JOIN servers ON domains.server_id = servers.id WHERE domains.name = '%s'"%(GL_ip2arpa(aDict['prefix'])))
  domains = db.get_rows()
 return domains

#
#
def domain_save(aDict, aCTX):
 """Function saves state and records for a domain, for dynamic DNS servers this is a No OP

 Args:
  - id (required)

 Output:
  - result
 """
 ret = {}
 id = aDict['id']
 with aCTX.db as db:
  db.do("SELECT foreign_id, server, node FROM servers LEFT JOIN domains ON domains.server_id = servers.id WHERE domains.id = %s"%id)
  infra = db.get_row()
  ret = aCTX.node_call(infra['node'],infra['server'],'domain_save',{'id':infra['foreign_id']})
 return {'result':ret['result']}

######################################## Records ####################################

#
#
def record_list(aDict, aCTX):
 """Function docstring for record_list TBD

 Args:
  - type (optional)
  - domain_id (required), <B>use cached one</B>

 Output:
 """
 with aCTX.db as db:
  if aDict.get('domain_id'):
   db.do("SELECT foreign_id, server, node FROM servers LEFT JOIN domains ON domains.server_id = servers.id WHERE domains.id = %s"%aDict['domain_id'])
   infra = db.get_row()
   aDict['domain_id'] = infra['foreign_id']
  else:
   # Strictly internal use - this one fetch all records for consistency check
   id = aDict.pop('server_id','0')
   db.do("SELECT server, node FROM servers WHERE id = %s"%id)
   infra = db.get_row()
 ret = aCTX.node_call(infra['node'],infra['server'],'record_list',aDict)
 ret['domain_id'] = aDict.get('domain_id',0)
 return ret

#
#
def record_info(aDict, aCTX):
 """Function docstring for record_info TBD

 Args:
  - id (required)
  - domain_id (required)

  - name (optional)
  - content (optional)
  - type (optional)

 Output:
 """
 ret = {}
 domain_id = aDict['domain_id']

 with aCTX.db as db:
  if aDict['id'] == 'new' and not (aDict.get('op') == 'update'):
   ret['data'] = {'id':'new','domain_id':domain_id,'name':'key','content':'value','type':'type-of-record','ttl':'3600','foreign_id':'NA'}
  else:
   db.do("SELECT foreign_id, server, node FROM servers LEFT JOIN domains ON domains.server_id = servers.id WHERE domains.id = %s"%domain_id)
   infra = db.get_row()
   aDict['domain_id'] = infra['foreign_id']
   ret = aCTX.node_call(infra['node'],infra['server'],'record_info',aDict)
   ret['data']['domain_id']  = domain_id
 return ret

#
#
def record_delete(aDict, aCTX):
 """Function docstring for record_delete TBD

 Args:
  - id (required)
  - domain_id (required)

 Output:
 """
 with aCTX.db as db:
  db.do("SELECT foreign_id, server, node FROM servers LEFT JOIN domains ON domains.server_id = servers.id WHERE domains.id = %s"%aDict['domain_id'])
  infra = db.get_row()
 aDict['domain_id'] = infra['foreign_id']
 ret = aCTX.node_call(infra['node'],infra['server'],'record_delete',aDict)
 return ret

################################## DEVICE FUNCTIONS ##################################
#
#
def record_device_correct(aDict, aCTX):
 """Function docstring for record_device_correct. Update IPAM with correct A/PTR records

 Args:
  - record_id (required)
  - device_id (required)
  - domain_id (required)
  - type (required)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  update = "a_id = '%(record_id)s', a_dom_id = %(domain_id)s"%aDict if aDict['type'].lower() == 'a' else "ptr_id = '%(record_id)s'"%aDict
  ret['update'] = db.do("UPDATE devices SET %s WHERE id = '%s'"%(update,aDict['device_id']))
 return ret

#
#
def record_device_delete(aDict, aCTX):
 """Function docstring for record_device_delete TBD

 Args:
  - a_id (optional) - id/0
  - ptr_id (optional) - id/0
  - a_domain_id (optional required)
  - ptr_domain_id (optional required)

 Output:
 """
 ret = {'A':0,'PTR':0}
 with aCTX.db as db:
  for tp in ['a','ptr']:
   domain_id = aDict.get('%s_domain_id'%tp)
   id = str(aDict.get('%s_id'%tp,'0'))
   if domain_id > 0 and id != '0':
    db.do("SELECT foreign_id, server, node FROM domains LEFT JOIN servers ON domains.server_id = servers.id WHERE domains.id = '%s'"%(domain_id))
    infra = db.get_row()
    args = {'id':id,'domain_id':infra['foreign_id']}
    ret[tp.upper()] = aCTX.node_call(infra['node'],infra['server'],'record_delete',args)['deleted']
 return ret

#
#
def record_device_update(aDict, aCTX):
 """Function docstring for record_device_update. Tries to update DNS server with new info and fetch A and PTR id if they exist... (None, A, A + PTR)
  "Tricky" part is when device MOVED from one domain to another AND this means server change, then we need to do delete first on old server. If IP address changed PTR might have moved.

 Args:
  - id (required)     - id/new. ID is used to detect if moving device between domains... i.e. to fetch old info
  - a_id (required)   - id/0/new
  - ptr_id (required) - id/0/new
  - hostname (required)

  - ip_new (required)
  - ip_old (optional required)
  - a_domain_id_old (optional required)
  - a_domain_id_new (required)

 Output:
 """
 ret  = {'A':{'found':False,'record_id':0,'domain_id':aDict['a_domain_id_new']},'PTR':{'found':False,'record_id':0},'server':{}}
 data = {}

 def GL_ip2ptr(addr):
  octets = addr.split('.')
  octets.reverse()
  octets.append("in-addr.arpa")
  return ".".join(octets)

 with aCTX.db as db:
  domains = {'name':{},'foreign_id':{}}
  db.do("SELECT domains.id AS domain_id, server_id, foreign_id, name, server, node FROM domains LEFT JOIN servers ON domains.server_id = servers.id")
  domains['id']   = db.get_dict('domain_id')
  for dom in domains['id'].values():
   domains['name'][dom['name']] = dom
   domains['foreign_id'][dom['foreign_id']] = dom

  #
  # A record: check if valid domain, then if not a_id == 'new' check if we moved to new server, if so delete record and set a_id to new
  #
  a_id  = 'new' if str(aDict['a_id']) == '0' else aDict['a_id']
  infra = domains['id'].get(int(aDict['a_domain_id_new']),None)

  if not infra:
   return ret

  if a_id != 'new':
   old = domains['id'].get(int(aDict.get('a_domain_id_old',0)),None)
   if old['server_id'] != infra['server_id']:
    ret['server']['A'] = aCTX.node_call(old['node'],old['server'],'record_delete',{'id':a_id})
    a_id = 'new'
   else:
    ret['server']['A'] = 'remain'
  fqdn  = "%s.%s"%(aDict['hostname'], infra['name'])
  data['A']= {'server':infra['server'], 'node':infra['node'], 'domain_id':infra['domain_id'],'args':{'type':'A','id':a_id, 'domain_id':infra['foreign_id'], 'content':aDict['ip_new'], 'name':fqdn}}

  #
  # PTR record:  check if valid domain, then check if moved to new server, if so record and set ptr_id to new
  #
  ptr_id = 'new' if str(aDict['ptr_id']) == '0' else aDict['ptr_id']
  ptr  = GL_ip2ptr(aDict['ip_new'])
  arpa = ptr.partition('.')[2]
  infra = domains['name'].get(arpa,None)
  if infra and fqdn:
   if ptr_id != 'new':
    old_ptr  = GL_ip2ptr(aDict['ip_old'])
    old_arpa = old_ptr.partition('.')[2]
    old = domains['name'].get(old_arpa,None)
    if old['server_id'] != infra['server_id']:
     ret['server']['PTR'] = aCTX.node_call(old['node'],old['server'],'record_delete',{'id':ptr_id})
     ptr_id = 'new'
    else:
     ret['server']['PTR'] = 'remain'
   data['PTR']= {'server':infra['server'], 'node':infra['node'], 'domain_id':infra['domain_id'], 'args':{'type':'PTR','id':ptr_id, 'domain_id':infra['foreign_id'], 'content':fqdn, 'name':ptr}}

 for type,infra in data.iteritems():
  if infra['server']:
   infra['args']['op'] = 'update'
   res = aCTX.node_call(infra['node'],infra['server'],'record_info',infra['args'])
   if not res['found']:
    # real 'op' should be insert as we now reset the record id to create new one
    infra['args']['id'] = 'new'
    res = aCTX.node_call(infra['node'],infra['server'],'record_info',infra['args'])
   if res['found']:
    ret[type]['found']     = True
    ret[type]['record_id'] = res['data']['id']
    ret[type]['domain_id'] = domains['foreign_id'].get(res['data']['domain_id'],{'domain_id':0})['domain_id']
    ret[type]['update']    = (res.get('update',0) == 1)
    ret[type]['insert']    = (res.get('insert',0) == 1)
 return ret

#
#
def record_device_create(aDict, aCTX):
 """Function docstring for record_device_create. The function actually only creates records for an existing device, and update the device..
 It does not expect 'overlapping' reverse or forwarding zones - hence bypassing IPAM's PTR registration and does lookup for first available reverse record

 Args:
  - device_id (required)
  - ip (required)
  - type (required)
  - domain_id (required)
  - fqdn (required)

 Output:
 """
 ret = {}
 args = {'op':'update','id':'new','type':aDict['type'].upper()}
 if args['type'] == 'A':
  args['name'] = aDict['fqdn']
  args['content'] = aDict['ip']
 elif args['type'] == 'PTR':
  def GL_ip2ptr(addr):
   octets = addr.split('.')
   octets.reverse()
   octets.append("in-addr.arpa")
   return ".".join(octets)
  args['name'] = GL_ip2ptr(aDict['ip'])
  args['content'] = aDict['fqdn']

 with aCTX.db as db:
  db.do("SELECT foreign_id, server, node FROM servers LEFT JOIN domains ON domains.server_id = servers.id WHERE domains.id = %s"%aDict['domain_id'])
  infra = db.get_row()
  args['domain_id'] = infra['foreign_id']
  ret['record'] = aCTX.node_call(infra['node'],infra['server'],'record_info',args)
  opres = str(ret['record'].get('update')) == "1" or str(ret['record'].get('insert')) == "1"
  if opres and (args['type'] in ['A','PTR']):
   ret['device'] = {'id':aDict['device_id']}
   ret['device']['update'] = db.do("UPDATE devices SET %s_id = '%s' WHERE id = %s"%(aDict['type'].lower(),ret['record']['data']['id'],aDict['device_id']))
 return ret

###################################### Tools ####################################
#
#
def status(aDict, aCTX):
 """Function docstring for top TBD

 Args:
  - count (optional)

 Output:
 """
 ret = {'top':{},'who':{}}
 args = {'count':aDict.get('count',20)}
 with aCTX.db as db:
  db.do("SELECT server, node FROM servers LEFT JOIN domains ON domains.server_id = servers.id WHERE servers.type = 'DNS'")
  servers = db.get_rows()
 for infra in servers:
  res = aCTX.node_call(infra['node'],infra['server'],'status',args)
  ret['top']["%(node)s_%(server)s"%infra] = res['top']
  ret['who']["%(node)s_%(server)s"%infra] = res['who']
 return ret

#
#
def consistency_check(aDict, aCTX):
 """Function docstring for consistency_check. Pulls all A and PTR records from domain servers, expects domain cache to be up-to-date

 Args:

 Output:
 """
 def GL_ip2arpa(addr):
  octets = addr.split('.')[:3]
  octets.reverse()
  octets.append("in-addr.arpa")
  return ".".join(octets)

 ret = {'records':[],'devices':[]}
 with aCTX.db as db:
  # Collect DNS severs
  db.do("SELECT id, server, node FROM servers WHERE type = 'DNS'")
  servers = db.get_dict('id')
  # Fetch domains
  db.do("SELECT id,foreign_id,name FROM domains")
  domains = db.get_dict('name')
  foreign = {}
  # Save domains foreign_ids to output
  for dom in domains.values():
   foreign[dom['foreign_id']] = {'id':dom['id'],'name':dom['name']}

  # Go through A and PTR records
  for type in ['a','ptr']:
   records = {}
   # Fetch records from each server
   for id,data in servers.iteritems():
    records[id] = record_list({'type':type,'server_id':id})['records']
   # Get 'type' data for all devices
   db.do("SELECT devices.id as device_id, a_dom_id, INET_NTOA(ia.ip) AS ip, %s_id AS record_id, CONCAT(hostname,'.',domains.name) AS fqdn FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN domains ON devices.a_dom_id = domains.id"%(type))
   devices = db.get_dict('ip' if type == 'a' else 'fqdn')

   # Now check them records for matching devices and translate domain_id into centralized cached one 
   for srv,recs in records.iteritems():
    for rec in recs:
     dev = devices.pop(rec['content'],{'record_id':0,'fqdn':None,'device_id':None,'a_dom_id':None})
     dom = foreign[rec['domain_id']]['id']
     if (dev['record_id'] != rec['id']) or (rec['type'] == 'A' and dom != dev['a_dom_id']):
      rec['server_id'] = srv
      rec['domain_id'] = dom
      # rec['fqdn'] = rec['content'] if rec['type'] == 'PTR' else rec['name']
      rec.update({'record_id':dev['record_id'],'fqdn':dev['fqdn'],'device_id':dev['device_id']})
      ret['records'].append(rec)
   # All devices that are left have no match
   for dev in devices.values():
    dev['type'] = type.upper()
    a_dom_id = dev.pop('a_dom_id','0')
    dev['domain_id'] = a_dom_id if type == 'a' else domains[GL_ip2arpa(dev['ip'])]['id']
    ret['devices'].append(dev)
 return ret

#
#
def external_ip(aDict, aCTX):
 """Function docstring for external_ip. TBD

 Args:

 Output:
 """
 from zdcp.core.genlib import external_ip
 return {'ip':external_ip() }
