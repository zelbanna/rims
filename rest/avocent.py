"""Avocent REST module. Provides calls to interact with avocent PDUs"""
__author__ = "Zacharias El Banna"
__version__ = "18.03.16"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from ..devices.avocent import Device

#
#
def update(aDict):
 """Function docstring for update TBD

 Args:
  - slot (required)
  - ip (required)
  - unit (required)
  - text (required)

 Output:
 """
 if not (int(aDict['slot']) == 0 and int(aDict['unit']) == 0):
  avocent = Device(aDict['ip'])
  ret = avocent.set_name(int(aDict['slot']),int(aDict['unit']),aDict['text'])
 else:
  ret = 'not updating 0.0'
 return ret

#
#
def info(aDict):
 """Function docstring for info TBD

 Args:
  - ip (required)
  - id (required)
  - op (optional)

 Output:
 """
 from ..core.common import DB
 ret = {}
 with DB() as db:
  if aDict.get('op') == 'lookup':
   pdu   = Device(aDict['ip'])
   slotl = pdu.get_slot_names()
   slotn = len(slotl)
   args = {'slots':slotn,'0_slot_id':slotl[0][0],'0_slot_name':slotl[0][1]}
   if slotn == 2:
    args.update({'1_slot_id':slotl[1][0],'1_slot_name':slotl[1][1]})
   db.update_dict('pduinfo',args,"device_id = %s"%aDict['id'])

  ret['xist'] = db.do("SELECT * FROM pduinfo WHERE device_id = '%s'"%aDict['id'])
  if ret['xist'] == 1:
   ret['data'] = db.get_row()
  else:
   db.do("INSERT INTO pduinfo SET device_id = %s, slots = 1"%(aDict['id']))
   ret['data'] = {'slots':1, '0_slot_id':0, '0_slot_name':'', '1_slot_id':1, '1_slot_name':'' }
 return ret

#
#
def inventory(aDict):
 """Function docstring for inventory TBD

 Args:
  - ip (required)

 Output:
 """
 avocent = Device(aDict['ip'])
 return avocent.get_inventory()

#
#
def op(aDict):
 """Function docstring for op TBD

 Args:
  - ip (required)
  - slot (required)
  - state (required)
  - unit (required)

 Output:
 """
 ret = {}
 avocent = Device(aDict['ip'])
 ret['op'] = avocent.set_state(aDict['slot'],aDict['unit'],aDict['state'])['res']
 from time import sleep
 sleep(10 if aDict['state'] == 'reboot' else 5)
 ret['state'] = avocent.get_state(aDict['slot'],aDict['unit'])['state']
 return ret
