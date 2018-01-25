"""Module docstring.

Avicent REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

from ..core.dbase import DB
from ..devices.avocent import Device

#
#
def update(aDict):
 avocent = Device(aDict['ip'])
 return avocent.set_name(int(aDict['slot']),int(aDict['unit']),aDict['text'])

#
#
def info(aDict):
 ret = {}
 with DB() as db:
  if aDict.get('op') == 'lookup':
   pdu   = Device(aDict['ip'])
   slotl = pdu.get_slot_names()
   slotn = len(slotl)
   if slotn == 1:
    db.do("UPDATE pduinfo SET slots = 1, 0_slot_id = '{}', 0_slot_name = '{}' WHERE device_id = {}".format(slotl[0][0],slotl[0][1],aDict['id']))
   elif slotn == 2:
    db.do("UPDATE pduinfo SET slots = 2, 0_slot_id = '{}', 0_slot_name = '{}', 1_slot_id = '{}', 1_slot_name = '{}' WHERE device_id = {}".format(slotl[0][0],slotl[0][1],slotl[1][0],slotl[1][1],aDict['id']))

  ret['xist'] = db.do("SELECT * FROM pduinfo WHERE device_id = '%s'"%aDict['id'])
  if ret['xist'] == 1:
   ret['data'] = db.get_row()
  else:
   db.do("INSERT INTO pduinfo SET device_id = %s, slots = 1"%(aWeb['id']))
   ret['data'] = {'slots':1, '0_slot_id':0, '0_slot_name':'', '1_slot_id':1, '1_slot_name':'' }
 return ret
