"""Module docstring.

SDCP DNS cache REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__ = "Production"

from ..core.dbase import DB
from .. import SettingsContainer as SC

#
#
def list_domains(aDict):
 """Function docstring for list_domains.

 Args:
  - filter (optional)
  - dict (optional)
  - sync (optional)

 Extra:
  - filter:forward/reverse
 """
 if SC.dns['node'] == 'master':
  from importlib import import_module
  module = import_module("sdcp.rest.%s"%SC.dns['type'])
  fun = getattr(module,'domains',None)
  ret = fun(aDict)
 else:
  from ..core.rest import call as rest_call
  ret = rest_call(SC.node[SC.dns['node']], "%s_domains"%(SC.dns['type']),aDict)['data']
 if aDict.get('sync'):
  ret.update({'added':[],'deleted':[]})
  with DB() as db:
   xist = db.do("SELECT domains.* FROM domains")
   cache = db.get_dict('id')
  for dom in ret['domains']:
   if not cache.pop(dom['id'],None):
    ret['added'].append(dom)
    db.do("INSERT INTO domains(id,name) VALUES ({0},'{1}') ON DUPLICATE KEY UPDATE name = '{1}'".format(dom['id'],dom['name']))
  for id,dom in cache.iteritems():
   ret['deleted'].append(dom)
   db.do("DELETE FROM domains WHERE id = '%s'"%id)
 return ret

#
#
def list_domains_cache(aDict):
 """Function docstring for list_domains_cache TBD

 Args:
  - filter (optional)
  - dict (optional)

 Extra:
 """
 ret = {}
 with DB() as db:
  if aDict.get('filter'):
   ret['xist'] = db.do("SELECT domains.* FROM domains WHERE name %s LIKE '%%arpa' ORDER BY name"%('' if aDict.get('filter') == 'reverse' else "NOT"))
  else:
   ret['xist'] = db.do("SELECT domains.* FROM domains")
  ret['domains'] = db.get_rows() if not aDict.get('dict') else db.get_dict(aDict.get('dict'))
 return ret

#
#
def domain_lookup(aDict):
 """Function docstring for domain_lookup TBD

 Args:
  - id (required)

 Extra:
 """
 if SC.dns['node'] == 'master':
  from importlib import import_module
  module = import_module("sdcp.rest.%s"%SC.dns['type'])
  fun = getattr(module,'domain_lookup',None)
  ret = fun({'id':aDict['id']})
 else:
  from ..core.rest import call as rest_call
  ret = rest_call(SC.node[SC.dns['node']], "%s_domain_lookup"%(SC.dns['type']),{'id':aDict['id']})['data']
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

 Extra:
 """
 if SC.dns['node'] == 'master':
  from importlib import import_module
  module = import_module("sdcp.rest.%s"%SC.dns['type'])
  fun = getattr(module,'domain_update',None)
  ret = fun(aDict)
 else:
  from ..core.rest import call as rest_call
  ret = rest_call(SC.node[SC.dns['node']], "%s_domain_update"%(SC.dns['type']),aDict)['data']
 return ret

#
#
def domain_delete(aDict):
 """Function docstring for domain_delete. Should cover nested case too TODO

 Args:
  - from (required)
  - to (required)

 Extra:
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
   if SC.dns['node'] == 'master':
    from importlib import import_module
    module = import_module("sdcp.rest.%s"%SC.dns['type'])
    fun = getattr(module,'domain_delete',None)
    ret.update(fun({'id':aDict['from']}))
   else:
    from ..core.rest import call as rest_call
    ret.update(rest_call(SC.node[SC.dns['node']], "%s_domain_delete"%(SC.dns['type']),{'id':aDict['from']})['data'])
 return ret

######################################## Records ####################################

#
#
def list_records(aDict):
 """Function docstring for list_records TBD

 Args:
  - type (optional)
  - domain_id (optional)

 Extra:
 """
 if SC.dns['node'] == 'master':
  from importlib import import_module
  module = import_module("sdcp.rest.%s"%SC.dns['type'])
  fun = getattr(module,'records',None)
  ret = fun(aDict)
 else:
  from ..core.rest import call as rest_call
  ret = rest_call(SC.node[SC.dns['node']], "%s_records"%(SC.dns['type']),aDict)['data']
 return ret

#
#
def record_lookup(aDict):
 """Function docstring for record_lookup TBD

 Args:
  - domain_id (required)
  - id (required)

 Extra:
 """
 if SC.dns['node'] == 'master':  
  from importlib import import_module  
  module = import_module("sdcp.rest.%s"%SC.dns['type'])  
  fun = getattr(module,'record_lookup',None)
  ret = fun({'domain_id':aDict['domain_id'],'id':aDict['id']})
 else:  
  from ..core.rest import call as rest_call
  ret = rest_call(SC.node[SC.dns['node']], "%s_record_lookup"%(SC.dns['type']),{'domain_id':aDict['domain_id'],'id':aDict['id']})['data']       
 return ret

#
#
def record_update(aDict):
 """Function docstring for record_update TBD

 Args:
  - id (required) - id/0/'new'
  - name (required)
  - content (required)
  - type (required)
  - domain_id (required)

 Extra:
 """
 if SC.dns['node'] == 'master':  
  from importlib import import_module  
  module = import_module("sdcp.rest.%s"%SC.dns['type'])  
  fun = getattr(module,'record_update',None)
  ret = fun(aDict)
 else:  
  from ..core.rest import call as rest_call
  ret = rest_call(SC.node[SC.dns['node']], "%s_record_update"%(SC.dns['type']),aDict)['data']
 return ret

#
#
def record_delete(aDict):
 """Function docstring for record_delete TBD

 Args:
  - id (required)

 Extra:
 """
 if SC.dns['node'] == 'master':  
  from importlib import import_module  
  module = import_module("sdcp.rest.%s"%SC.dns['type'])  
  fun = getattr(module,'record_delete',None)
  ret = fun({'id':aDict['id']})
 else:  
  from ..core.rest import call as rest_call
  ret = rest_call(SC.node[SC.dns['node']], "%s_record_delete"%(SC.dns['type']),{'id':aDict['id']})['data']       
 return ret

#
#
def record_transfer(aDict):
 """Function docstring for record_transfer. Update IPAM device with correct A/PTR records

 Args:
  - record_id (required)
  - device_id (required)
  - type (required)

 Extra:
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

 Extra:
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
 if SC.dns['node'] == 'master':  
  from importlib import import_module  
  module = import_module("sdcp.rest.%s"%SC.dns['type'])  
  fun = getattr(module,'record_update',None)
  ret['dns'] = fun(args)
 else:  
  from ..core.rest import call as rest_call
  ret['dns'] = rest_call(SC.node[SC.dns['node']], "%s_record_update"%(SC.dns['type']),args)['data']
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

 Extra:
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

 if SC.dns['node'] == 'master':  
  from importlib import import_module  
  module = import_module("sdcp.rest.%s"%SC.dns['type'])  
  fun = getattr(module,'record_update',None)
  for arg in args.values():
   ret[arg['type']] = fun(arg)
 else:  
  from ..core.rest import call as rest_call
  for arg in args.values():
   ret[arg['type']] = rest_call(SC.node[SC.dns['node']], "%s_record_update"%(SC.dns['type']),arg)['data']
 return ret

#
#
def record_device_delete(aDict):
 """Function docstring for record_device_delete TBD

 Args:
  - a_id (optional) - id/0
  - ptr_id (optional) - id/0

 Extra:
 """
 ret = {}
 if SC.dns['node'] == 'master':
  from importlib import import_module
  module = import_module("sdcp.rest.%s"%SC.dns['type'])
  fun = getattr(module,'record_delete',None)
  for tp in ['A','PTR']:
   ret[tp] = fun({'id':aDict.get(tp)})['deleted'] if str(aDict.get(tp,'0')) != '0' else None
 else:
  from ..core.rest import call as rest_call
  for tp in ['A','PTR']:
   ret[tp] = rest_call(SC.node[SC.dns['node']], "%s_record_delete"%(SC.dns['type']),{'id':aDict.get(tp)})['data']['deleted'] if str(aDict.get(tp,'0')) != '0' else None
 return ret


###################################### Tools ####################################

#
#
def dedup(aDict):
 """Function docstring for dedup. TBD

 Args:

 Extra:
 """
 if SC.dns['node'] == 'master':  
  from importlib import import_module  
  module = import_module("sdcp.rest.%s"%SC.dns['type'])  
  fun = getattr(module,'dedup',None)
  ret = fun({})
 else:  
  from ..core.rest import call as rest_call
  ret = rest_call(SC.node[SC.dns['node']], "%s_dedup"%(SC.dns['type']))['data']
 return ret

#
#
def top(aDict):
 """Function docstring for top TBD

 Args:
  - count (optional)

 Extra:
 """
 if SC.dns['node'] == 'master':  
  from importlib import import_module  
  module = import_module("sdcp.rest.%s"%SC.dns['type'])  
  fun = getattr(module,'top',None)
  ret = fun(aDict)
 else:  
  from ..core.rest import call as rest_call
  ret = rest_call(SC.node[SC.dns['node']], "%s_top"%(SC.dns['type']),aDict)['data']
 return ret

#
#
def consistency(aDict):
 """Function docstring for consistency. Pulls all A and PTR records from domain server, expects domain cache to be up-to-date

 Args:

 Extra:
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
   records = list_records({'type':type})['records']
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
