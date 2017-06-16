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

#
# Update PDU slot info for a device
#
def update_device_pdus(aDict):
 hostname  = aDict.get('hostname')
 ret = {}
 db = GL.DB()
 db.connect()
 for p in ['0','1']:
  ret[p] = None
  id = aDict.get("pem{}_pdu_id".format(p))
  if id:
   slot = aDict.get("pem{}_pdu_slot".format(p))
   unit = aDict.get("pem{}_pdu_unit".format(p))
   if not (slot == 0 or unit == 0):
    from sdcp.devices.RackUtils import Avocent
    db.do("SELECT INET_NTOA(ip) as ip FROM pdus WHERE id = '{}'".format(id))
    pdu = db.get_row()
    avocent = Avocent(pdu['ip'])
    ret["pem{}".format(p)] = avocent.set_name(slot,unit,hostname+"-P{}".format(p))
 db.close()
 return ret
