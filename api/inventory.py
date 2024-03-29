"""Inventory API module."""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

############################################### INVENTORY ################################################
#
#
def list(aRT, aArgs):
 """ Function retrives the inventory

 Args:
  - search (optional) content to search 'field' on
  - field (optional required) search field
  - extra (optional) list of extra columns to add to list
  - sort (optional). sort order, default is 'serial'
  - dict (optional) (output as dictionary instead of list)

 Output:
 """
 ret = {}
 sort = 'ORDER BY inv.%s'%aArgs.get('sort','serial')
 fields = ['inv.id','inv.model','inv.serial']
 tables = ['inventory AS inv']
 flter = ['TRUE']

 if 'search' in aArgs:
  flter.append("inv.%(field)s LIKE '%%%(search)s%%'"%aArgs)

 if 'extra' in aArgs:
  fields.extend(['inv.%s'%x for x in aArgs['extra']])

 with aRT.db as db:
  ret['count'] = db.query("SELECT %s FROM %s WHERE %s %s"%(", ".join(fields),' LEFT JOIN '.join(tables),' AND '.join(flter),sort))
  ret['data'] = db.get_rows() if 'dict' not in aArgs else db.get_dict(aArgs['dict'])
 return ret

#
#
def vendor_list(aRT, aArgs):
 """Function retrieves vendors in inventory

 Args:

 Output:
 """
 ret = {}
 with aRT.db as db:
  ret['count'] = db.query("SELECT vendor, count(*) AS count FROM inventory GROUP BY vendor")
  ret['data']  = db.get_rows()
 return ret

#
#
def info(aRT, aArgs):
 """ Function operates on inventory items

 Args:
  - id
  - op (optional)
  - device_id (optional)
  - serial (optional)
  - model  (optional)
  - license (optional). Bool
  - license_key (optinal). License key
  - support_contract (optional). Bool
  - support_end_date (optional). Date
  - description    (optional)
  - purchase_order (optional)
  - location (optional)
  - comments (optional)

 Output:
 """
 ret = {}
 id = aArgs.pop('id','new')
 op = aArgs.pop('op',None)
 with aRT.db as db:
  if op == 'update':
   for tp in ['license','support_contract']:
    x = aArgs.get(tp,0)
    aArgs[tp] = 1 if x in (True, '1', 1) else 0

   for tp in ['receive_date','support_end_date']:
    if tp in aArgs and aArgs[tp] == '':
     aArgs.pop(tp,None)

   if id != 'new':
    ret['update'] = db.update_dict('inventory',aArgs,'id=%s'%id)
   else:
    ret['update'] = db.insert_dict('inventory',aArgs)
    id = db.get_last_id() if ret['update'] > 0 else 'new'

  if id != 'new':
   ret['found'] = (db.query("SELECT * FROM inventory WHERE id = '%s'"%id) == 1)
   ret['data'] = db.get_row()
   ret['data']['receive_date'] = str(ret['data']['receive_date']) if ret['data']['receive_date'] else None
   ret['data']['support_end_date'] = str(ret['data']['support_end_date']) if ret['data']['support_end_date'] else None
   for tp in ['license','support_contract']:
    ret['data'][tp] = (ret['data'][tp] == 1)
  else:
   ret['found'] = True
   ret['data'] = {'id':'new','vendor':'','serial':'','model':'','license':False,'license_key':'','support_contract':False,'support_end_date':'','description':'N/A','purchase_order':'','location_id':None,'receive_date':'','product':'','comments':''}
  db.query("SELECT id,name FROM locations")
  ret['locations'] = db.get_rows()
 return ret

#
#
def delete(aRT, aArgs):
 """Function deleted an inventory item

 Args:
  - id (required)

 Output:
  - deleted (bool)
 """
 with aRT.db as db:
  res = (db.execute("DELETE FROM inventory WHERE id = %s"%aArgs['id']) == 1)
 return {'deleted':res}
