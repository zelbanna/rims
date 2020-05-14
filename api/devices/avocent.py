"""Avocent REST module. Provides calls to interact with avocent PDUs"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

from rims.devices.avocent import Device

#
#
def update(aCTX, aArgs):
 """Function docstring for update TBD

 Args:
  - device_id (required)
  - slot (required)
  - unit (required)
  - text (required)

 Output:
 """
 ret = {}
 if not (int(aArgs['slot']) == 0 and int(aArgs['unit']) == 0):
  avocent = Device(aCTX, aArgs['device_id'])
  ret = avocent.set_name(int(aArgs['slot']),int(aArgs['unit']),aArgs['text'])
 else:
  ret['info'] = 'not updating 0.0'
  ret['status'] = 'NOT_OK'
 return ret

#
#
def info(aCTX, aArgs):
 """Function docstring for info TBD

 Args:
  - device_id (required)
  - op (optional)

 Output:
  - info
 """
 ret = {}
 with aCTX.db as db:
  if aArgs.get('op') == 'lookup':
   pdu = Device(aCTX,aArgs['device_id'])
   slots = pdu.get_slot_names()
   args = {'slots':len(slots)}
   if args['slots'] > 0:
    for i,slot in enumerate( slots ):
     args['%d_slot_id'%i]   = slot[0]
     args['%d_slot_name'%i] = slot[1]
    db.update_dict('pdu_info',args,"device_id = %s"%aArgs['device_id'])

  if (db.do("SELECT * FROM pdu_info WHERE device_id = '%(device_id)s'"%aArgs) > 0):
   ret['data'] = db.get_row()
  else:
   db.do("INSERT INTO pdu_info SET device_id = %(device_id)s, slots = 1"%aArgs)
   ret['data'] = {'slots':1, '0_slot_id':0, '0_slot_name':"", '1_slot_id':1, '1_slot_name':"" }
 return ret

#
#
def inventory(aCTX, aArgs):
 """Function docstring for inventory TBD

 Args:
  - device_id (required)

 Output:
  - data. list of inventory items
 """
 ret = {}
 avocent = Device(aCTX,aArgs['device_id'])
 try:    ret['data'] = avocent.get_inventory()
 except: ret['status'] = 'NOT_OK'
 else:   ret['status'] = 'OK'
 return ret

#
#
def op(aCTX, aArgs):
 """Function docstring for op TBD

 Args:
  - device_id (required)
  - slot (required)
  - state (required)
  - unit (required)

 Output:
  - status. Operation status
  - state. New state
 """
 from time import sleep
 avocent = Device(aCTX,aArgs['device_id'])
 ret = avocent.set_state(aArgs['slot'],aArgs['unit'],aArgs['state'])
 sleep(10)
 ret['state'] = avocent.get_state(aArgs['slot'],aArgs['unit'])['state']
 return ret
