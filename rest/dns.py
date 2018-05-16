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

def __rest_format__(aFunction):
 return "%s?%s_%s&node=%s"%(SC['node'][SC['dns']['node']], SC['dns']['type'], aFunction, SC['dns']['node'])


#
#
def server_list(aDict):
 """Function docstring for server_list TBD

 Args:

 Output:
 """
 ret = {}
 with DB() as db:
  db.do("SELECT domain_servers.id,type, nodes.node AS node FROM domain_servers LEFT JOIN nodes ON domain_servers.node_id = nodes.id")
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
  db.do("SELECT id,node FROM nodes")
  ret['types'] = ['powerdns','infoblox']
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
   ret['data'] = {'id':'new','node_id':None,'type':'Unknown'}
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

#
#
def domain_list(aDict):
 """Function docstring for domain_list.

 Args:
  - filter (optional)
  - dict (optional)
  - sync (optional)

 Output:
  - filter:forward/reverse
 """
 ret = {}
 with DB() as db:
  if aDict.get('sync') == 'true':
   org = {}
   db.do("SELECT domain_servers.id, type, nodes.node, nodes.url FROM domain_servers LEFT JOIN nodes ON domain_servers.node_id = nodes.id")
   servers = db.get_rows()
   for server in servers:
    if SC['system']['id'] == server['node']:
     module = import_module("sdcp.rest.%s"%server['type'])
     fun = getattr(module,'domains',None)
     org[server['id']] = fun({})['domains']
    else:
     org[server['id']] = rest_call("%s?%s_domains&node=%s"%(server['url'],server['type'],server['node']))['data']['domains']
   ret.update({'sync':{'added':[],'deleted':[]}})
   db.do("SELECT domains.* FROM domains")
   cache = db.get_dict('id')
   for srv,domains in org.iteritems():
    for dom in domains:
     if not cache.pop(dom['id'],None):
      ret['sync']['added'].append(dom)
      # Add forward here
      db.insert_dict('domains',{'id':dom['id'],'name':dom['name'],'server_id':srv},"ON DUPLICATE KEY UPDATE name = '%s'"%dom['name'])
    for id,dom in cache.iteritems():
     ret['sync']['deleted'].append(dom)
     db.do("DELETE FROM domains WHERE id = '%s'"%id)

  if aDict.get('filter'):
   ret['xist'] = db.do("SELECT domains.*, domain_servers.type AS server FROM domains LEFT JOIN domain_servers ON domains.server_id = domain_servers.id WHERE name %s LIKE '%%arpa' ORDER BY name"%('' if aDict.get('filter') == 'reverse' else "NOT"))
  else:      
   ret['xist'] = db.do("SELECT domains.*, domain_servers.type AS server FROM domains LEFT JOIN domain_servers ON domains.server_id = domain_servers.id")
  ret['domains'] = db.get_rows() if not aDict.get('dict') else db.get_dict(aDict.get('dict'))
 return ret

#
#
def domain_lookup(aDict):
 """Function docstring for domain_lookup TBD

 Args:
  - id (required)

 Output:
 """
 if SC['dns'].get('node',SC['system']['id']) == SC['system']['id']:
  module = import_module("sdcp.rest.%s"%SC['dns']['type'])
  fun = getattr(module,'domain_lookup',None)
  ret = fun({'id':aDict['id']})
 else:
  ret = rest_call(__rest_format__('domain_lookup'),{'id':aDict['id']})['data']
 return ret

#
#
def domain_update(aDict):
 """Function docstring for domain_update TBD

 Args:
  - type (required)
  - master (required)
  - id (required)
  - name (required)

 Output:
 """
 if SC['dns'].get('node',SC['system']['id']) == SC['system']['id']:
  module = import_module("sdcp.rest.%s"%SC['dns']['type'])
  fun = getattr(module,'domain_update',None)
  ret = fun(aDict)
 else:
  ret = rest_call(__rest_format__('domain_update'),aDict)['data']
 return ret

#
#
def domain_delete(aDict):
 """Function docstring for domain_delete. Should cover nested case too TODO

 Args:
  - from (required)
  - to (required)

 Output:
 """
 ret = {'result':'NOT_OK'}
 with DB() as db:
  try:
   ret['transfer'] = db.do("UPDATE devices SET a_dom_id = %s WHERE a_dom_id = %s"%(aDict['to'],aDict['from']))
   ret['deleted']  = db.do("DELETE FROM domains WHERE id = %s"%(aDict['from']))
   ret['result']   = 'OK'
  except:
   pass
  else:
   if SC['dns'].get('node',SC['system']['id']) == SC['system']['id']:
    module = import_module("sdcp.rest.%s"%SC['dns']['type'])
    fun = getattr(module,'domain_delete',None)
    ret.update(fun({'id':aDict['from']}))
   else:
    ret.update(rest_call(__rest_format__('domain_delete'),{'id':aDict['from']})['data'])
 return ret

######################################## Records ####################################

#
#
def record_list(aDict):
 """Function docstring for record_list TBD

 Args:
  - type (optional)
  - domain_id (optional)

 Output:
 """
 if SC['dns'].get('node',SC['system']['id']) == SC['system']['id']:
  module = import_module("sdcp.rest.%s"%SC['dns']['type'])
  fun = getattr(module,'records',None)
  ret = fun(aDict)
 else:
  ret = rest_call(__rest_format__('records'),aDict)['data']
 return ret

#
#
def record_lookup(aDict):
 """Function docstring for record_lookup TBD

 Args:
  - id (required)
  - domain_id (optional)

 Output:
 """
 args = {'domain_id':aDict.get('domain_id'),'id':aDict['id']}
 if SC['dns'].get('node',SC['system']['id']) == SC['system']['id']:
  module = import_module("sdcp.rest.%s"%SC['dns']['type'])  
  fun = getattr(module,'record_lookup',None)
  ret = fun(args)
 else:  
  ret = rest_call(__rest_format__('record_lookup'),args)['data']       
 return ret

#
#
def record_update(aDict):
 """Function docstring for record_update TBD

 Args:
  - id (required)
  - name (required)
  - content (required)
  - type (required)
  - domain_id (required)

 Output:
 """
 if SC['dns'].get('node',SC['system']['id']) == SC['system']['id']:
  module = import_module("sdcp.rest.%s"%SC['dns']['type'])  
  fun = getattr(module,'record_update',None)
  ret = fun(aDict)
 else:  
  ret = rest_call(__rest_format__('record_update'),aDict)['data']
 return ret

#
#
def record_delete(aDict):
 """Function docstring for record_delete TBD

 Args:
  - id (required)

 Output:
 """
 if SC['dns'].get('node',SC['system']['id']) == SC['system']['id']:
  module = import_module("sdcp.rest.%s"%SC['dns']['type'])  
  fun = getattr(module,'record_delete',None)
  ret = fun({'id':aDict['id']})
 else:  
  ret = rest_call(__rest_format__('record_delete'),{'id':aDict['id']})['data']       
 return ret

#
#
def record_transfer(aDict):
 """Function docstring for record_transfer. Update IPAM device with correct A/PTR records

 Args:
  - record_id (required)
  - device_id (required)
  - type (required)

 Output:
 """
 with DB() as db:
  update = db.do("UPDATE devices SET %s_id = '%s' WHERE id = '%s'"%(aDict['type'].lower(),aDict['record_id'],aDict['device_id']))
 return {'transfered':update}

#
#
def record_device_create(aDict):
 """Function docstring for record_device_create TBD

 Args:
  - ip (required)
  - type (required)
  - domain_id (required)
  - fqdn (required)

 Output:
 """
 ret = {'result':'OK'}
 args = {'id':'new','domain_id':aDict['domain_id'],'type':aDict['type'].upper()}
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
 if SC['dns'].get('node',SC['system']['id']) == SC['system']['id']:
  module = import_module("sdcp.rest.%s"%SC['dns']['type'])  
  fun = getattr(module,'record_update',None)
  ret['dns'] = fun(args)
 else:  
  ret['dns'] = rest_call(__rest_format__('record_update'),args)['data']
 if str(ret['dns']['update']) == "1" and (args['type'] == 'A' or args['type'] == 'PTR'):
  ret['device'] = {'id':aDict['id']}
  with DB() as db:
   ret['update'] = db.do("UPDATE devices SET %s_id = '%s' WHERE id = '%s'"%(aDict['type'].lower(),ret['dns']['id'],aDict['id']))
 return ret

#
#
def record_device_update(aDict):
 """Function docstring for record_device_update TBD

 Args:
  - ip (required)
  - hostname (required)
  - a_domain_id (required)
  - a_id (required)   - id/0
  - ptr_id (required) - id/0

 Output:
 """
 ret = {}
 def GL_ip2ptr(addr):
  octets = addr.split('.')
  octets.reverse()
  octets.append("in-addr.arpa")
  return ".".join(octets)

 ptr  = GL_ip2ptr(aDict['ip'])
 arpa = ptr.partition('.')[2]
 args = {'A':{'type':'A','id':aDict['a_id'],'content':aDict['ip'],'domain_id':aDict['a_domain_id']},'PTR':{'type':'PTR','id':aDict['ptr_id'],'name':ptr}}

 with DB() as db:
  db.do("SELECT id,name FROM domains WHERE id = '%s' OR name = '%s'"%(aDict['a_domain_id'],arpa))
  domains = db.get_rows()
  for domain in domains:
   if domain['id'] == int(aDict['a_domain_id']):
    fqdn = "%s.%s"%(aDict['hostname'],domain['name'])
    args['A']['name'] = fqdn
    args['PTR']['content'] = fqdn 
   elif domain['name'] == arpa:
    args['PTR']['domain_id'] = domain['id']

 if SC['dns'].get('node',SC['system']['id']) == SC['system']['id']:
  module = import_module("sdcp.rest.%s"%SC['dns']['type'])  
  fun = getattr(module,'record_update',None)
  for arg in args.values():
   ret[arg['type']] = fun(arg)
 else:  
  for arg in args.values():
   ret[arg['type']] = rest_call(__rest_format__('record_update'),arg)['data']
 return ret

#
#
def record_device_delete(aDict):
 """Function docstring for record_device_delete TBD

 Args:
  - a_id (optional) - id/0
  - ptr_id (optional) - id/0

 Output:
 """
 ret = {}
 if SC['dns'].get('node',SC['system']['id']) == SC['system']['id']:
  module = import_module("sdcp.rest.%s"%SC['dns']['type'])
  fun = getattr(module,'record_delete',None)
  for tp in ['A','PTR']:
   ret[tp] = fun({'id':aDict.get(tp)})['deleted'] if str(aDict.get(tp,'0')) != '0' else None
 else:
  for tp in ['A','PTR']:
   ret[tp] = rest_call(__rest_format__('record_delete'),{'id':aDict.get(tp)})['data']['deleted'] if str(aDict.get(tp,'0')) != '0' else None
 return ret


###################################### Tools ####################################

#
#
def dedup(aDict):
 """Function docstring for dedup. TBD

 Args:

 Output:
 """
 if SC['dns'].get('node',SC['system']['id']) == SC['system']['id']:
  module = import_module("sdcp.rest.%s"%SC['dns']['type'])  
  fun = getattr(module,'dedup',None)
  ret = fun({})
 else:  
  ret = rest_call(__rest_format__('dedup'))['data']
 return ret

#
#
def top(aDict):
 """Function docstring for top TBD

 Args:
  - count (optional)

 Output:
 """
 if SC['dns'].get('node',SC['system']['id']) == SC['system']['id']:
  module = import_module("sdcp.rest.%s"%SC['dns']['type'])  
  fun = getattr(module,'top',None)
  ret = fun(aDict)
 else:  
  ret = rest_call(__rest_format__('top'),aDict)['data']
 return ret

#
#
def consistency(aDict):
 """Function docstring for consistency. Pulls all A and PTR records from domain server, expects domain cache to be up-to-date

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
  db.do("SELECT id,name FROM domains WHERE name LIKE '%%in-addr.arpa'")
  domains = db.get_dict('name')
  for type in ['a','ptr']:
   records = record_list({'type':type})['records']
   db.do("SELECT devices.id as device_id, a_dom_id, INET_NTOA(ip) AS ipasc, %s_id AS dns_id, CONCAT(hostname,'.',domains.name) AS fqdn FROM devices LEFT JOIN domains ON devices.a_dom_id = domains.id"%(type))
   devices = db.get_dict('ipasc' if type == 'a' else 'fqdn')
   for rec in records:
    dev = devices.pop(rec['content'],None)
    if not dev or dev['dns_id'] != rec['id']:
     rec.update(dev if dev else {'dns_id':None,'fqdn':None})
     ret['records'].append(rec)
   for dev in devices.values():
    dev['type'] = type.upper()
    dev['domain_id'] = dev['a_dom_id'] if type == 'a' else domains[GL_ip2arpa(dev['ipasc'])]['id']
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
