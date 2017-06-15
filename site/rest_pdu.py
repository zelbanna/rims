"""Moduledocstring.

REST calls module

"""
__author__= "Zacharias El Banna"                     
__version__ = "17.6.1GA"
__status__= "Production"

import sdcp.core.GenLib as GL

#
# Update PDU slot info (name basically)
#
def unit_update(aDict):
 if aDict.get('name'):
  from sdcp.devices.RackUtils import Avocent
  name = aDict.get('name')
  pdu  = aDict.get('pdu','0')
  slot = aDict.get('slot','0')
  unit = aDict.get('unit','0')
  avocent = Avocent(pdu)
  res = avocent.set_name(slot,unit,name)
  return { 'res':'op_success', 'info':res }
 else:
  return { 'res':'op_failed' }

#
# Update PDU slot info for a device
#
def update_device_pdus(aDict):
 from sdcp.devices.RackUtils import Avocent
 pem0_id   = aDict.get('pem0_id')
 pem1_id   = aDict.get('pem1_id')
 pem0_slot = aDict.get('pem0_slot')
 pem1_slot = aDict.get('pem1_slot')
 pem0_unit = aDict.get('pem0_unit')
 pem1_unit = aDict.get('pem1_unit')
 hostname  = aDict.get('hostname')
 ret = {'pem0':None,'pem1':None}
 db = GL.DB()
 db.connect()
 sql = "SELECT id,INET_NTOA(ip) as ip FROM pdus WHERE id = '{}' OR id = '{}'".format(pem0_id,pem1_id)
 db.do(sql)
 pdus = db.get_all_dict('id')
 if pem0_id and not (pem0_slot == 0 or pem0_unit == 0):
  avocent = Avocent(pdus[int(pem0_id)]['ip'])
  ret['pem0'] = avocent.set_name(pem0_slot,pem0_unit,hostname+"-P0")
 if pem1_id and not (pem1_slot == 0 or pem1_unit == 0):
  avocent = Avocent(pdus[int(pem1_id)]['ip'])
  ret['pem1'] = avocent.set_name(pem1_slot,pem1_unit,hostname+"-P1")
 db.close()
 return ret

#
# Remove PDU from DB
#
def remove(aDict):
 id = aDict.get('id')
 db = GL.DB()
 db.connect()
 db.do("UPDATE rackinfo SET pem0_pdu_unit = 0, pem0_pdu_slot = 0 WHERE pem0_pdu_id = '{0}'".format(id))
 db.do("UPDATE rackinfo SET pem1_pdu_unit = 0, pem1_pdu_slot = 0 WHERE pem1_pdu_id = '{0}'".format(id))
 db.do("DELETE FROM pdus WHERE id = '{0}'".format(id))
 db.commit()
 db.close()
 return { 'res':'op_success' }
