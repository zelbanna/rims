"""Avocent REST module. Provides calls to interact with avocent PDUs"""
__author__ = "Zacharias El Banna"
__version__ = "4.0GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from zdcp.devices.avocent import Device

#
#
def update(aDict, aCTX):
 """Function docstring for update TBD

 Args:
  - slot (required)
  - ip (required)
  - unit (required)
  - text (required)

 Output:
 """
 if not (int(aDict['slot']) == 0 and int(aDict['unit']) == 0):
  avocent = Device(aDict['ip'],gSettings)
  ret = avocent.set_name(int(aDict['slot']),int(aDict['unit']),aDict['text'])
 else:
  ret = 'not updating 0.0'
 return ret

#
#
def info(aDict, aCTX):
 """Function docstring for info TBD

 Args:
  - ip (required)
  - id (required)
  - op (optional)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  if aDict.get('op') == 'lookup':
   pdu = Device(aDict['ip'],gSettings)
   slotl = pdu.get_slot_names()
   slotn = len(slotl)
   args = {'slots':slotn,'0_slot_id':slotl[0][0],'0_slot_name':slotl[0][1]}
   if slotn == 2:
    args.update({'1_slot_id':slotl[1][0],'1_slot_name':slotl[1][1]})
   db.update_dict('pdu_info',args,"device_id = %(id)s"%aDict)

  ret['found'] = (db.do("SELECT * FROM pdu_info WHERE device_id = '%(id)s'"%aDict) > 0)
  if ret['found']:
   ret['data'] = db.get_row()
  else:
   db.do("INSERT INTO pdu_info SET device_id = %(id)s, slots = 1"%aDict)
   ret['data'] = {'slots':1, '0_slot_id':0, '0_slot_name':'', '1_slot_id':1, '1_slot_name':'' }
 return ret

#
#
def inventory(aDict, aCTX):
 """Function docstring for inventory TBD

 Args:
  - ip (required)

 Output:
 """
 avocent = Device(aDict['ip'],gSettings)
 return avocent.get_inventory()

#
#
def op(aDict, aCTX):
 """Function docstring for op TBD

 Args:
  - ip (required)
  - slot (required)
  - state (required)
  - unit (required)

 Output:
 """
 ret = {}
 avocent = Device(aDict['ip'],gSettings)
 ret['op'] = avocent.set_state(aDict['slot'],aDict['unit'],aDict['state'])['res']
 from time import sleep
 sleep(10 if aDict['state'] == 'reboot' else 5)
 ret['state'] = avocent.get_state(aDict['slot'],aDict['unit'])['state']
 return ret
