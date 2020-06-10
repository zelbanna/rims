"""Location API module."""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

############################################### INVENTORY ################################################
#
#
def list(aCTX, aArgs):
 """ Function retrives locations

 Args:
  - dict (optional)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  ret['count'] = db.query("SELECT * FROM locations")
  ret['data'] =  db.get_rows() if not 'dict' in aArgs else db.get_dict(aArgs['dict'])
 return ret

#
#
def info(aCTX, aArgs):
 """ Function operates on location items

 Args:
  - id (required)
  - op (optional)
  - name (optional)

 Output:
 """
 ret = {}
 id = aArgs.pop('id','new')
 op = aArgs.pop('op',None)
 with aCTX.db as db:
  if op == 'update':
   if not id == 'new':
    ret['update'] = db.update_dict('locations',aArgs,'id=%s'%id)
   else:
    ret['insert'] = db.insert_dict('locations',aArgs)
    id = db.get_last_id() if ret['insert'] > 0 else 'new'

  ret['data'] = db.get_row() if  not id == 'new' and (db.query("SELECT id,name FROM locations WHERE id = '%s'"%id) > 0) else {'id':'new','name':''}
 return ret

#
#
def delete(aCTX, aArgs):
 """ Function deletes a location

 Args:
  - id (required)

 Output:
 """
 ret = {}
 # Racks and inventory sets NULL anyway
 with aCTX.db as db:
  ret['deleted'] = (db.execute("DELETE FROM locations WHERE id = %s"%aArgs['id']) == 1)
  ret['status'] = 'OK' if ret['deleted'] else 'NOT_OK'
 return ret
