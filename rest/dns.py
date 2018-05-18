"""DNS API module. This module is a REST wrapper for interfaces to a particular DNS server (device) type module.           
Settings:
 - node
 - type

"""
__author__ = "Zacharias El Banna"
__version__ = "18.04.07GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from sdcp.core.common import DB,SC,rest_call

################################ SERVERS ##################################
#
#
def server_list(aDict):
 """Function docstring for server_list TBD

 Args:

 Output:
 """
 ret = {}
 with DB() as db:
  db.do("SELECT id, server, node FROM domain_servers")
  ret['servers']= db.get_rows()
 return ret

#
#
def server_info(aDict):
 """Function docstring for server_info TBD

 Args:

 Output:
 """
 ret = {}
 args = aDict
 id = args.pop('id','new')
 op = args.pop('op',None)
 with DB() as db:
  ret['servers'] = [{'server':'local'},{'server':'powerdns'},{'server':'infoblox'}]
  db.do("SELECT node FROM nodes")
  ret['nodes'] = db.get_rows()
  if op == 'update':
   if not id == 'new':
    ret['update'] = db.update_dict('domain_servers',args,"id=%s"%id) 
   else:
    ret['update'] = db.insert_dict('domain_servers',args)
    id = db.get_last_id() if ret['update'] > 0 else 'new'

  if not id == 'new':
   ret['xist'] = db.do("SELECT * FROM domain_servers WHERE id = '%s'"%id)
   ret['data'] = db.get_row()
  else:
   ret['data'] = {'id':'new','node':None,'server':'Unknown'}
 return ret

#
#
def server_delete(aDict):
 """Function docstring for server_delete TBD

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with DB() as db:
  ret['deleted'] = db.do("DELETE FROM domain_servers WHERE id = %s"%aDict['id'])
 return ret

################################ Domains ##################################
#
#
def domain_list(aDict):
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
 with DB() as db:
  if aDict.get('sync') == 'true':
   org = {}
   db.do("SELECT id, server, node FROM domain_servers")
   servers = db.get_rows()
   for server in servers:
    if SC['system']['id'] == server['node']:
     module = import_module("sdcp.rest.%s"%server['server'])
     fun = getattr(module,'domain_list',None)
     org[server['id']] = fun({})['domains']
    else:
     org[server['id']] = rest_call("%s?%s_domain_list"%(SC['node'][server['node']],server['server']))['data']['domains']
   ret.update({'sync':{'added':[],'deleted':[]}})
   db.do("SELECT domains.* FROM domains")
   cache = db.get_dict('foreign_id')
   for srv,domains in org.iteritems():
    for dom in domains:
     if not cache.pop(dom['id'],None):
      ret['sync']['added'].append(dom)
      # Add forward here
      db.insert_dict('domains',{'name':dom['name'],'server_id':srv,'foreign_id':dom['id']},"ON DUPLICATE KEY UPDATE name = '%s'"%dom['name'])
   for id,dom in cache.iteritems():
    ret['sync']['deleted'].append(dom)
    db.do("DELETE FROM domains WHERE id = '%s'"%id)

  filter = []
  if aDict.get('filter'):
   filter.append("name %s LIKE '%%arpa'"%('' if aDict.get('filter') == 'reverse' else "NOT"))
  if aDict.get('exclude'):
   db.do("SELECT server_id FROM domains WHERE id = '%s'"%(aDict.get('exclude')))
   filter.append('server_id = %s'%(db.get_val('server_id')))
   filter.append("domains.id <> '%s'"%aDict.get('exclude'))

  ret['xist'] = db.do("SELECT domains.*, server FROM domains LEFT JOIN domain_servers ON domains.server_id = domain_servers.id WHERE %s ORDER BY name"%('TRUE' if len(filter) == 0 else " AND ".join(filter)))
  ret['domains'] = db.get_rows() if not aDict.get('dict') else db.get_dict(aDict.get('dict'))
 return ret

#
#
def domain_info(aDict):
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
 args = aDict
 with DB() as db:
  if args['id'] == 'new' and not (args.get('op') == 'update'):
   db.do("SELECT id, server, node FROM domain_servers")
   ret['servers'] = db.get_rows()
   ret['data'] = {'id':'new','name':'new-name','master':'ip-of-master','type':'MASTER', 'notified_serial':0 }
  else:
   if args['id'] == 'new':
    db.do("SELECT id, 'new' AS foreign_id, server, node FROM domain_servers WHERE id = %s"%args.pop('server_id','0'))
   else:
    db.do("SELECT domain_servers.id, foreign_id, server, node FROM domain_servers LEFT JOIN domains ON domains.server_id = domain_servers.id WHERE domains.id = %s"%args['id'])
   ret['infra'] = db.get_row()
   args['id']   = ret['infra'].pop('foreign_id',None)
   if SC['system']['id'] == ret['infra']['node']:
    module = import_module("sdcp.rest.%s"%ret['infra']['server'])
    fun = getattr(module,'domain_info',None)
    ret.update(fun(args))
   else:
    ret.update(rest_call("%s?%s_domain_info"%(SC['node'][ret['infra']['node']],ret['infra']['server']),args)['data'])
   if str(ret.get('insert',0)) == '1':
    ret['cache'] = db.insert_dict('domains',{'name':args['name'],'server_id':ret['infra']['id'],'foreign_id':ret['data']['id']})
    ret['id'] = db.get_last_id() 
 return ret

#
#
def domain_delete(aDict):
 """Function docstring for domain_delete.

 Args:
  - id (required)
  - transfer (optional)

 Output:
 """
 ret = {}
 if aDict['id'] != aDict.get('transfer'):
  with DB() as db:
   db.do("SELECT foreign_id, server, node FROM domain_servers LEFT JOIN domains ON domains.server_id = domain_servers.id WHERE domains.id = '%s'"%aDict['id'])
   infra = db.get_row()
   if SC['system']['id'] == infra['node']:
    module = import_module("sdcp.rest.%s"%infra['server'])
    fun = getattr(module,'domain_delete',None)
    res = fun({'id':infra['foreign_id']})
   else:
    res = rest_call("%s?%s_domain_delete"%(SC['node'][infra['node']],infra['server']),{'id':infra['foreign_id']})['data']
   ret.update(res)
   ret['devices'] = db.do("UPDATE devices SET a_id = 0, a_dom_id = '%s' WHERE a_dom_id = %s"%(aDict.get('transfer',0),aDict['id']))
   ret['cache']   = db.do("DELETE FROM domains WHERE id = %s"%(aDict['id']))
 return ret

######################################## Records ####################################

#
#
def record_list(aDict):
 """Function docstring for record_list TBD

 Args:
  - type (optional)
  - domain_id (optional required)
  - server_id (optional required)

 Output:
 """
 args = aDict
 with DB() as db:
  if aDict.get('domain_id'):
   db.do("SELECT foreign_id, server, node FROM domain_servers LEFT JOIN domains ON domains.server_id = domain_servers.id WHERE domains.id = %s"%aDict['domain_id'])
   infra = db.get_row()
   args['domain_id'] = infra['foreign_id'] 
  else:
   id = aDict.pop('server_id','0')
   db.do("SELECT server, node FROM domain_servers WHERE id = %s"%id)
   infra = db.get_row()
  
 if SC['system']['id'] == infra['node']:
  module = import_module("sdcp.rest.%s"%infra['server'])
  fun = getattr(module,'record_list',None)
  ret = fun(args)
 else:
  ret = rest_call("%s?%s_record_list"%(SC['node'][infra['node']],infra['server']),args)['data']
 return ret

#
#
def record_info(aDict):
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
 args = aDict
 with DB() as db:
  db.do("SELECT foreign_id, server, node FROM domain_servers LEFT JOIN domains ON domains.server_id = domain_servers.id WHERE domains.id = %s"%args['domain_id'])
  infra = db.get_row()
  if aDict['id'] == 'new' and not (aDict.get('op') == 'update'):
   ret['data'] = {'id':'new','domain_id':infra['foreign_id'],'name':'key','content':'value','type':'type-of-record','ttl':'3600'}
  else:
   args['domain_id'] = infra['foreign_id']
   if SC['system']['id'] == infra['node']:
    module = import_module("sdcp.rest.%s"%infra['server'])
    fun = getattr(module,'record_info',None)
    ret = fun(args)
   else:
    ret = rest_call("%s?%s_record_info"%(SC['node'][infra['node']],infra['server']),args)['data']
  return ret

#
#
def record_delete(aDict):
 """Function docstring for record_delete TBD

 Args:
  - id (required)
  - domain_id (required)

 Output:
 """
 args = aDict
 with DB() as db:
  db.do("SELECT foreign_id, server, node FROM domain_servers LEFT JOIN domains ON domains.server_id = domain_servers.id WHERE domains.id = %s"%args['domain_id'])
  infra = db.get_row()
 args['domain_id'] = infra['foreign_id']
 if SC['system']['id'] == infra['node']:
  module = import_module("sdcp.rest.%s"%infra['server'])
  fun = getattr(module,'record_delete',None)
  ret = fun(args)
 else:
  ret = rest_call("%s?%s_record_delete"%(SC['node'][infra['node']],infra['server']),args)['data']
 return ret

################################## DEVICE FUNCTIONS ##################################
#
#
def record_device_correct(aDict):
 """Function docstring for record_device_correct. Update IPAM with correct A/PTR records

 Args:
  - record_id (required)
  - device_id (required)
  - domain_id (required)
  - type (required)

 Output:
 """
 ret = {}
 with DB() as db:
  update = "a_id = '%s', a_dom_id ='%s'"%(aDict['record_id'],aDict['domain_id']) if aDict['type'].lower() == 'a' else "ptr_id = '%s'"%aDict['record_id']
  ret['update'] = db.do("UPDATE devices SET %s WHERE id = '%s'"%(update,aDict['device_id']))
 return ret

#
#
def record_device_delete(aDict):
 """Function docstring for record_device_delete TBD

 Args:
  - a_id (optional) - id/0
  - ptr_id (optional) - id/0
  - a_domain_id (optional required)
  - ptr_domain_id (optional required)

 Output:
 """
 ret = {'A':None,'PTR':None}
 with DB() as db:
  for tp in ['a','ptr']:
   domain_id = aDict.get('%s_domain_id'%tp)
   id = str(aDict.get('%s_id'%tp,'0'))
   if domain_id and id != '0':
    db.do("SELECT foreign_id, server, node FROM domains LEFT JOIN domain_servers ON domains.server_id = domain_servers.id WHERE domains.id = '%s'"%(domain_id))
    infra = db.get_row()
    args = {'id':id,'domain_id':infra['foreign_id']}
    if SC['system']['id'] == infra['node']:
     module = import_module("sdcp.rest.%s"%infra['server'])
     fun = getattr(module,'record_delete',None)
     ret[tp.upper()] = fun(args)['deleted']
    else:
     ret[tp.upper()] = rest_call("%s?%s_record_delete"%(SC['node'][infra['node']],infra['server']),args)['data']['deleted']
 return ret

#
#
def record_device_update(aDict):
 """Function docstring for record_device_update. Tries to update DNS server with new info and fetch A and PTR id if they exist... (None, A, A + PTR)
  "Tricky" part is when device MOVED from one domain to another AND this means server change, then we need to do delete first on old server. If IP address changed.

 Args:
  - id (required) id/new
  - ip (required)
  - hostname (required)
  - a_domain_id (required)
  - a_id (required)   - id/0/new
  - ptr_id (required) - id/0/new

 Output:
 """
 from json import dumps
 from sdcp.core.logger import log
 log("dns_record_device_update '%s'"%dumps(aDict))
 ret  = {'A':{'xist':0},'PTR':{'xist':0},'device':{'xist':0},'server':{}}
 aDict['a_domain_id'] = int(aDict['a_domain_id'])
 data = {}

 def _record_delete(server,node,id):
  if SC['system']['id'] == node:
   module = import_module("sdcp.rest.%s"%server)
   fun = getattr(module,'record_delete',None)
   ret = fun({'id':id})
  else:
   ret = rest_call("%s?%s_record_delete"%(SC['node'][node],server),{'id':id})['data']
  return ret

 def GL_ip2ptr(addr):
  octets = addr.split('.')
  octets.reverse()
  octets.append("in-addr.arpa")
  return ".".join(octets)

 with DB() as db:
  domains = {'name':{},'foreign_id':{}}
  db.do("SELECT domains.id AS domain_id, server_id, foreign_id, name, server, node FROM domains LEFT JOIN domain_servers ON domains.server_id = domain_servers.id")
  domains['id']   = db.get_dict('domain_id')
  for dom in domains['id'].values():
   domains['name'][dom['name']] = dom
   domains['foreign_id'][dom['foreign_id']] = dom

  ret['device']['xist'] = db.do("SELECT hostname, a_dom_id AS a_domain_id, INET_NTOA(ip) AS ip FROM devices WHERE id = '%s'"%(aDict['id'])) if not aDict['id'] == 'new' else 0
  device = db.get_row() if ret['device']['xist'] > 0 else None
  #
  # A record: check if valid domain, then if not a_id == 'new' make sure we didn't move server otherwise delete record and set a_id to new
  #
  a_id  = 'new' if str(aDict['a_id']) == '0' else aDict['a_id']
  infra = domains['id'].get(aDict['a_domain_id'],None)
  
  if not infra:
   return ret

  if a_id != 'new' and device:
   old = domains['id'].get(device['a_domain_id'],None) 
   if old['server_id'] != infra['server_id']:
    ret['server']['A'] = _record_delete(old['server'],old['node'],a_id)
    a_id = 'new'
   else:
    ret['server']['A'] = 'remain'
  fqdn  = "%s.%s"%(aDict['hostname'], infra['name'])
  data['A']= {'server':infra['server'], 'node':infra['node'], 'args':{'type':'A','id':a_id, 'domain_id':infra['foreign_id'], 'content':aDict['ip'], 'name':fqdn}}

  #
  # PTR record:  check if valid domain, then if not a_id == 'new' make sure we didn't move server otherwise delete record and set ptr_id to new
  # 
  ptr_id = 'new' if str(aDict['ptr_id']) == '0' else aDict['ptr_id']
  ptr  = GL_ip2ptr(aDict['ip'])
  arpa = ptr.partition('.')[2]
  infra = domains['name'].get(arpa,None)
  if infra and fqdn:
   if ptr_id != 'new' and device:
    old_ptr  = GL_ip2ptr(device['ip'])
    old_arpa = ptr.partition('.')[2]
    old = domains['name'].get(old_arpa,None)
    if old['server_id'] != infra['server_id']:
     ret['server']['PTR'] = _record_delete(old['server'],old['node'],ptr_id)
     ptr_id = 'new'
    else:
     ret['server']['PTR'] = 'remain'
   data['PTR']= {'server':infra['server'], 'node':infra['node'], 'args':{'type':'PTR','id':ptr_id, 'domain_id':infra['foreign_id'], 'content':fqdn, 'name':ptr}}

 for type,infra in data.iteritems():
  if infra['server']:
   infra['args']['op'] = 'update'
   if SC['system']['id'] == infra['node']:
    module = import_module("sdcp.rest.%s"%infra['server'])  
    fun = getattr(module,'record_info',None)
    res = fun(infra['args'])
   else:
    res = rest_call("%s?%s_record_info"%(SC['node'][infra['node']],infra['server']),infra['args'])['data']
   
   ret[type]['record_id'] = res['data']['id']
   ret[type]['domain_id'] = domains['foreign_id'].get(res['data']['domain_id'],{'domain_id':0})['domain_id']
   ret[type]['xist'] = res['xist']
   ret[type]['update'] = res.get('update',0)
   ret[type]['insert'] = res.get('insert',0)
 return ret

#
#
def record_device_create(aDict):
 """Function docstring for record_device_create TBD

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

 with DB() as db: 
  db.do("SELECT foreign_id, server, node FROM domain_servers LEFT JOIN domains ON domains.server_id = domain_servers.id WHERE domains.id = %s"%aDict['domain_id'])
  infra = db.get_row()
  args['domain_id'] = infra['foreign_id']
  if SC['system']['id'] == infra['node']:
   module = import_module("sdcp.rest.%s"%infra['server'])
   fun = getattr(module,'record_info',None)
   ret['record'] = fun(args)
  else:
   ret['record'] = rest_call("%s?%s_record_info"%(SC['node'][infra['node']],infra['server']),args)['data']

  opres = str(ret['record'].get('update')) == "1" or str(ret['record'].get('insert')) == "1"
  if opres and (args['type'] in ['A','PTR']):
   ret['device'] = {'id':aDict['device_id']}
   ret['device']['update'] = db.do("UPDATE devices SET %s_id = '%s' WHERE id = '%s'"%(aDict['type'].lower(),ret['record']['data']['id'],aDict['device_id']))
 return ret

###################################### Tools ####################################

#
#
def dedup(aDict):
 """Function docstring for dedup. TBD

 Args:

 Output:

 """
 ret = {}
 with DB() as db: 
  db.do("SELECT server, node FROM domain_servers LEFT JOIN domains ON domains.server_id = domain_servers.id")
  servers = db.get_rows()
 for infra in servers:
  if SC['system']['id'] == infra['node']:
   module = import_module("sdcp.rest.%s"%infra['server'])  
   fun = getattr(module,'dedup',None)
   res = fun({})
  else:  
   res = rest_call("%s?%s_dedup"%(SC['node'][infra['node']],infra['server']))['data']
  ret["%s_%s"%(infra['node'],infra['server'])] = res['removed']
 return ret

#
#
def top(aDict):
 """Function docstring for top TBD

 Args:
  - count (optional)

 Output:
 """
 ret = {'top':{},'who':{}}
 args = {'count':aDict.get('count',20)}
 with DB() as db: 
  db.do("SELECT server, node FROM domain_servers LEFT JOIN domains ON domains.server_id = domain_servers.id")
  servers = db.get_rows()
 for infra in servers:
  if SC['system']['id'] == infra['node']:
   module = import_module("sdcp.rest.%s"%infra['server'])  
   fun = getattr(module,'top',None)
   res = fun(args)
  else:  
   res = rest_call("%s?%s_top"%(SC['node'][infra['node']],infra['server']),args)['data']
  ret['top']["%s_%s"%(infra['node'],infra['server'])] = res['top']
  ret['who']["%s_%s"%(infra['node'],infra['server'])] = res['who']
 return ret

#
#
def consistency_check(aDict):
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
 with DB() as db:
  # Collect DNS severs
  db.do("SELECT id, server, node FROM domain_servers")
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
   db.do("SELECT devices.id as device_id, a_dom_id, INET_NTOA(ip) AS ipasc, %s_id AS record_id, CONCAT(hostname,'.',domains.name) AS fqdn FROM devices LEFT JOIN domains ON devices.a_dom_id = domains.id"%(type))
   devices = db.get_dict('ipasc' if type == 'a' else 'fqdn')
 
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
    dev['domain_id'] = a_dom_id if type == 'a' else domains[GL_ip2arpa(dev['ipasc'])]['id']
    ret['devices'].append(dev)
 return ret

#
#
def external_ip(aDict):
 """Function docstring for external_ip. TBD

 Args:

 Output:
 """
 from sdcp.core.genlib import external_ip
 return {'ip':external_ip() }
