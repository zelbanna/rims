"""Avocent REST module. Provides calls to interact with avocent PDUs"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

from rims.devices.avocent import Device

#
#
def update(aCTX, aArgs = None):
 """Function docstring for update TBD

 Args:
  - id (required)
  - slot (required)
  - unit (required)
  - text (required)

 Output:
 """
 ret = {}
 if not (int(aArgs['slot']) == 0 and int(aArgs['unit']) == 0):
  avocent = Device(aCTX, aArgs['id'])
  ret = avocent.set_name(int(aArgs['slot']),int(aArgs['unit']),aArgs['text'])
 else:
  ret['info'] = 'not updating 0.0'
  ret['status'] = 'NOT_OK'
 return ret

#
#
def info(aCTX, aArgs = None):
 """Function docstring for info TBD

 Args:
  - id (required)
  - op (optional)

 Output:
  - info
 """
 ret = {}
 with aCTX.db as db:
  if aArgs.get('op') == 'lookup':
   pdu = Device(aCTX,aArgs['id'])
   slots = pdu.get_slot_names()
   args = {'slots':len(slots)}
   if args['slots'] > 0:
    for i,slot in enumerate( slots ):
     args['%d_slot_id'%i]   = slot[0]
     args['%d_slot_name'%i] = slot[1]
    db.update_dict('pdu_info',args,"device_id = %s"%aArgs['id'])

  ret['found'] = (db.do("SELECT * FROM pdu_info WHERE device_id = '%(id)s'"%aArgs) > 0)
  if ret['found']:
   ret['data'] = db.get_row()
  else:
   db.do("INSERT INTO pdu_info SET device_id = %(id)s, slots = 1"%aArgs)
   ret['data'] = {'slots':1, '0_slot_id':0, '0_slot_name':"", '1_slot_id':1, '1_slot_name':"" }
 return ret

#
#
def inventory(aCTX, aArgs = None):
 """Function docstring for inventory TBD

 Args:
  - id (required)

 Output:
  - data. list of inventory items
 """
 ret = {}
 avocent = Device(aCTX,aArgs['id'])
 try:    ret['data'] = avocent.get_inventory()
 except: ret['status'] = 'NOT_OK'
 else:   ret['status'] = 'OK'
 return ret

#
#
def op(aCTX, aArgs = None):
 """Function docstring for op TBD

 Args:
  - id (required)
  - slot (required)
  - state (required)
  - unit (required)

 Output:
  - status. Operation status
  - state. New state
 """
 from time import sleep
 ret = {}
 avocent = Device(aCTX,aArgs['id'])
 ret['status'] = avocent.set_state(aArgs['slot'],aArgs['unit'],aArgs['state'])
 sleep(10)
 ret['state'] = avocent.get_state(aArgs['slot'],aArgs['unit'])['state']
 return ret
