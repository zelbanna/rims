"""Module docstring.

SDCP DNS cache REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__ = "Production"

from ..core.dbase import DB

def load(aDict):
 ret = {'added':[],'deleted':[]}
 if aDict.get('domains'):
  with DB() as db:
   ret['cache'] = db.do("SELECT id,name FROM domains")
   cache = db.get_dict('id')
   for dom in aDict['domains']:
    if not cache.pop(dom['id'],None):
     ret['added'].append(dom)
     db.do("INSERT INTO domains(id,name) VALUES ({0},'{1}') ON DUPLICATE KEY UPDATE name = '{1}'".format(dom['id'],dom['name']))
  for id,dom in cache.iteritems():
   ret['deleted'].append(dom)
   db.do("DELETE FROM domains WHERE id = '%s'"%id)
 return ret
 
#
# filter:forward/reverse, index
def domains(aDict):
 ret = {}
 with DB() as db:
  if aDict.get('filter'):
   ret['xist'] = db.do("SELECT domains.* FROM domains WHERE name %s LIKE '%%arpa' ORDER BY name"%('' if aDict['filter'] == 'reverse' else "NOT"))
  else:
   ret['xist'] = db.do("SELECT domains.* FROM domains")
  if aDict.get('index'):
   ret['domains'] = db.get_dict(aDict['index'])
  else:
   ret['domains'] = db.get_rows()
 return ret

#
#
def domain_delete(aDict):
 ret = {'result':'NOT_OK'}
 if aDict.get('to') and aDict.get('from'):
  with DB() as db:
   try:
    ret['transfer'] = db.do("UPDATE devices SET a_dom_id = %s WHERE a_dom_id = %s"%(aDict['to'],aDict['from']))
    ret['deleted']  = db.do("DELETE FROM domains WHERE id = %s"%(aDict['from']))
    ret['result']   = 'OK'
   except: pass
 return ret

#
#
def domain_add(aDict):
 ret = {}
 with DB() as db:
  ret['xist'] = db.do("INSERT INTO domains SET id = %s, name = '%s'"%(aDict['id'],aDict['name']))
 return ret
