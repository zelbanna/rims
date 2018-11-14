"""Avocent REST module. Provides calls to interact with avocent PDUs"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

from rims.devices.avocent import Device

#
#
def update(aCTX, aArgs = None):
 """Function docstring for update TBD

 Args:
  - slot (required)
  - ip (required)
  - unit (required)
  - text (required)

 Output:
 """
 if not (int(aArgs['slot']) == 0 and int(aArgs['unit']) == 0):
  avocent = Device(aCTX, aArgs['ip'])
  ret = avocent.set_name(int(aArgs['slot']),int(aArgs['unit']),aArgs['text'])
 else:
  ret = 'not updating 0.0'
 return ret

#
#
def info(aCTX, aArgs = None):
 """Function docstring for info TBD

 Args:
  - ip (required)
  - id (required)
  - op (optional)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  if aArgs.get('op') == 'lookup':
   pdu = Device(aCTX,aArgs['ip'])
   slotl = pdu.get_slot_names()
   slotn = len(slotl)
   args = {'slots':slotn,'0_slot_id':slotl[0][0],'0_slot_name':slotl[0][1]}
   if slotn == 2:
    args.update({'1_slot_id':slotl[1][0],'1_slot_name':slotl[1][1]})
   db.update_dict('pdu_info',args,"device_id = %(id)s"%aArgs)

  ret['found'] = (db.do("SELECT * FROM pdu_info WHERE device_id = '%(id)s'"%aArgs) > 0)
  if ret['found']:
   ret['data'] = db.get_row()
  else:
   db.do("INSERT INTO pdu_info SET device_id = %(id)s, slots = 1"%aArgs)
   ret['data'] = {'slots':1, '0_slot_id':0, '0_slot_name':'', '1_slot_id':1, '1_slot_name':'' }
 return ret

#
#
def inventory(aCTX, aArgs = None):
 """Function docstring for inventory TBD

 Args:
  - ip (required)

 Output:
 """
 avocent = Device(aCTX,aArgs['ip'])
 return avocent.get_inventory()

#
#
def op(aCTX, aArgs = None):
 """Function docstring for op TBD

 Args:
  - ip (required)
  - slot (required)
  - state (required)
  - unit (required)

 Output:
 """
 from time import sleep
 ret = {}
 avocent = Device(aCTX,aArgs['ip'])
 ret['op'] = avocent.set_state(aArgs['slot'],aArgs['unit'],aArgs['state'])
 sleep(10)
 ret['state'] = avocent.get_state(aArgs['slot'],aArgs['unit'])['state']
 return ret
