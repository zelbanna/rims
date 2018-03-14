"""Settings REST module. Manages settings for nodes"""
__author__ = "Zacharias El Banna"
__version__ = "18.03.14GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from ..core.common import DB,SC

def list(aDict):
 """Function docstring for list TBD

 Args:
  - node (optional)
  - dict (optional)
  - section (optional)
  - user_id (optional)

 Output:
 """
 ret = {'user_id':aDict.get('user_id',"1"),'node':aDict.get('node',SC.system['id']) }
 if aDict.get('section'):
  filter = "AND section = '%s'"%aDict.get('section')
  ret['section'] = aDict.get('section')
 else:
  filter = ""
  ret['section'] = 'all'
 with DB() as db:
  ret['xist'] = db.do("SELECT * FROM settings WHERE node = '%s' %s ORDER BY section,parameter"%(ret['node'],filter))
  ret['data'] = db.get_dict(aDict.get('dict')) if aDict.get('dict') else db.get_rows()
 return ret

#
#
def info(aDict):
 """Function docstring for info TBD

 Args:
  - node (required)
  - id (required)
  - op (optional)
  - description (cond required)
  - section (cond required)
  - value (cond required)
  - parameter (cond required)

 Output:
 """
 ret = {}
 args = aDict
 id = args.pop('id',None)
 op = args.pop('op',None)
 with DB() as db:
  if op == 'update' and not (aDict['section'] == 'system' or aDict['section'] =='node'):
   if not id == 'new':
    ret['update'] = db.update_dict('settings',args,"id=%s"%id) 
   else:
    ret['update'] = db.insert_dict('settings',args)
    id = db.get_last_id()
  ret['xist'] = db.do("SELECT * FROM settings WHERE id = '%s'"%id)
  ret['data'] = db.get_row()
 return ret

#
#
def parameter(aDict):
 """Function docstring for parameter TBD

 Args:
  - node (required)
  - section (required)
  - parameter (required)

 Output:
 """
 ret = {}
 with DB() as db:
  ret['xist'] = db.do("SELECT * FROM settings WHERE node='%s' AND section='%s' AND parameter='%s'"%(aDict['node'],aDict['section'],aDict['parameter']))
  ret['data'] = db.get_row()
 return ret

#
#
def section(aDict):
 """Function docstring for section TBD

 Args:
  - node (required)
  - section (required)

 Output:
 """
 ret = {}
 with DB() as db:
  ret['xist'] = db.do("SELECT id,parameter,value,description FROM settings WHERE node = '%s' AND section = '%s' ORDER BY parameter"%(aDict['node'],aDict['section']))
  ret['data'] = db.get_dict('parameter')
 return ret

#
#
def all(aDict):
 """Function docstring for all TBD

 Args:
  - node (required)
  - dict (optional)
  - section (optional)

 Output:
 """
 ret = {}
 with DB() as db:
  if not aDict.get('section'):
   db.do("SELECT DISTINCT section FROM settings WHERE node='%s'"%aDict['node'])
   rows = db.get_rows()
   sections = [row['section'] for row in rows]
  else:
   sections = [aDict.get('section')]
  for section in sections:
   db.do("SELECT parameter,id,value,description FROM settings WHERE node = '%s' AND section = '%s'  ORDER BY parameter"%(aDict['node'],section))
   ret[section] = db.get_rows() if not aDict.get('dict') else db.get_dict(aDict.get('dict'))
 return ret

#
#
def delete(aDict):
 """Function docstring for delete TBD

 Args:
  - node (required)
  - id (required)

 Output:
 """
 ret = {} 
 with DB() as db:
  ret['deleted'] = db.do("DELETE FROM settings WHERE id = '%s' AND node = '%s'"%(aDict['id'],aDict['node']))
 return ret
