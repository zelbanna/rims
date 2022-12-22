"""Location API module."""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

############################################### INVENTORY ################################################
#
#
def list(aRT, aArgs):
 """ Function retrives locations

 Args:
  - dict (optional)

 Output:
 """
 ret = {}
 with aRT.db as db:
  ret['count'] = db.query("SELECT * FROM locations")
  ret['data'] =  db.get_rows() if not 'dict' in aArgs else db.get_dict(aArgs['dict'])
 return ret

#
#
def info(aRT, aArgs):
 """ Function operates on location items

 Args:
  - id (required)
  - op (optional)
  - name (optional)

 Output:
 """
 ret = {}
 lid = aArgs.pop('id','new')
 op = aArgs.pop('op',None)
 with aRT.db as db:
  if op == 'update':
   if lid != 'new':
    ret['update'] = db.update_dict('locations',aArgs,f"id={lid}")
   else:
    ret['insert'] = db.insert_dict('locations',aArgs)
    lid = db.get_last_id() if ret['insert'] > 0 else 'new'

  ret['data'] = db.get_row() if lid != 'new' and db.query("SELECT id,name FROM locations WHERE id = '%s'"%lid) else {'id':'new','name':''}
 return ret

#
#
def delete(aRT, aArgs):
 """ Function deletes a location

 Args:
  - id (required)

 Output:
 """
 ret = {}
 # Racks and inventory sets NULL anyway
 with aRT.db as db:
  ret['deleted'] = bool(db.execute(f"DELETE FROM locations WHERE id = {aArgs['id']}"))
  ret['status'] = 'OK' if ret['deleted'] else 'NOT_OK'
 return ret
