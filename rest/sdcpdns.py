"""Module docstring.

SDCP DNS cache REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

from ..core.dbase import DB

#
#
def domains(aDict):
 with DB() as db:
  db.do("SELECT id, name FROM domains")
  local = db.get_dict('id')
 return local

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
