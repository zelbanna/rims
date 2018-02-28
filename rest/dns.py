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
  from ..core.rest import call
  ret = call(SC.node[SC.dns['node']], "%s_domains"%(SC.dns['type']),aDict)['data']
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
def domain_lookup(aDict):
 if SC.dns['node'] == 'master':
  from importlib import import_module
  module = import_module("sdcp.rest.%s"%SC.dns['type'])
  fun = getattr(module,'domain_lookup',None)
  ret = fun({'id':aDict['id']})
 else:
  from ..core.rest import call
  ret = call(SC.node[SC.dns['node']], "%s_domain_lookup"%(SC.dns['type']),{'id':aDict['id']})['data']
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
  from ..core.rest import call
  ret = call(SC.node[SC.dns['node']], "%s_domain_update"%(SC.dns['type']),aDict)['data']
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
    from ..core.rest import call
    ret.update(call(SC.node[SC.dns['node']], "%s_domain_delete"%(SC.dns['type']),{'id':aDict['from']})['data'])
 return ret

######################################## Records ####################################

#
#
def list_records(aDict):
 """Function docstring for records TBD

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
  from ..core.rest import call
  ret = call(SC.node[SC.dns['node']], "%s_records"%(SC.dns['type']),aDict)['data']
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
  from ..core.rest import call
  ret = call(SC.node[SC.dns['node']], "%s_record_lookup"%(SC.dns['type']),{'domain_id':aDict['domain_id'],'id':aDict['id']})['data']       
 return ret

#
#
def record_auto_create(aDict):
 """Function docstring for record_auto_create TBD

 Args:
  - id (required)
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
  from ..core.rest import call
  ret['dns'] = call(SC.node[SC.dns['node']], "%s_record_update"%(SC.dns['type']),args)['data']
 if str(ret['dns']['xist']) == "1" and (args['type'] == 'A' or args['type'] == 'PTR'):
  ret['device'] = {'id':aDict['id']}
  with DB() as db:
   ret['xist'] = db.do("UPDATE devices SET %s_id = '%s' WHERE id = '%s'"%(aDict['type'].lower(),ret['dns']['id'],aDict['id']))
 return ret

#
#
def record_auto_delete(aDict):
 ret = {}
 if SC.dns['node'] == 'master':
  from importlib import import_module
  module = import_module("sdcp.rest.%s"%SC.dns['type'])
  fun = getattr(module,'record_delete',None)
  for tp in ['a','ptr']:
   ret[tp] = fun({'id':aDict.get(tp)})['deleted'] if str(aDict.get(tp,'0')) != '0' else None
 else:
  from ..core.rest import call
  for tp in ['a','ptr']:
   ret[tp] = call(SC.node[SC.dns['node']], "%s_record_delete"%(SC.dns['type']),{'id':aDict.get(tp)})['data']['deleted'] if str(aDict.get(tp,'0')) != '0' else None
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
  from ..core.rest import call
  ret = call(SC.node[SC.dns['node']], "%s_record_update"%(SC.dns['type']),aDict)['data']
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
  from ..core.rest import call
  ret = call(SC.node[SC.dns['node']], "%s_record_delete"%(SC.dns['type']),{'id':aDict['id']})['data']       
 return ret

#
#
def record_transfer(aDict):
 """Function docstring for record_transfer. Update IPAM device with correct A/PTR records

 Args:
  - record_id (required)
  - device_id (required)
  - type (required

 Extra:
 """
 with DB() as db:
  xist = db.do("UPDATE devices SET %s_id = '%s' WHERE id = '%s'"%(aDict['type'],aDict['record_id'],aDict['device_id']))
 return {'xist':xist}

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
  from ..core.rest import call
  ret = call(SC.node[SC.dns['node']], "%s_dedup"%(SC.dns['type']))['data']
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
  from ..core.rest import call
  ret = call(SC.node[SC.dns['node']], "%s_top"%(SC.dns['type']),aDict)['data']
 return ret
