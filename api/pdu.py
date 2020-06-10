"""PDU API module. Implements PDU methods"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

#
#
def list(aCTX, aArgs):
 """List PDUs

 Args:
  - empty (optional) bool

 Output:
  - data
 """
 ret = {}
 with aCTX.db as db:
  db.query("SELECT pi.*, devices.hostname AS name FROM pdu_info AS pi LEFT JOIN devices ON pi.device_id = devices.id")
  ret['data'] = db.get_rows()
  if aArgs.get('empty'):
   ret['data'].insert(0,{ 'name':'No PDU','device_id':'NULL', 'slots':1, '0_slot_id':0, '0_slot_name':'N/A','1_slot_id':1,'1_slot_name':'N/A'})
 return ret
