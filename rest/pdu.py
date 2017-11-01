"""Moduledocstring.

PDU REST calls module

"""
__author__= "Zacharias El Banna"                     
__version__ = "17.10.4"
__status__= "Production"

#
# Update PDU slot info (name basically)
#
def unit_update(aDict):
 if aDict.get('name'):
  from sdcp.devices.avocent import Device
  name = aDict.get('name')
  ip   = aDict.get('pdu')
  slot = aDict.get('slot','0')
  unit = aDict.get('unit','0')
  avocent = Device(ip)
  res = avocent.set_name(slot,unit,name)
  return { 'res':'op_success', 'info':res }
 else:
  return { 'res':'op_failed' }

#
# Remove PDU from DB
#
def remove(aDict):
 from sdcp.core.dbase import DB
 id = aDict.get('id')
 with DB() as db:
  db.do("UPDATE rackinfo SET pem0_pdu_unit = 0, pem0_pdu_slot = 0 WHERE pem0_pdu_id = '{0}'".format(id))
  db.do("UPDATE rackinfo SET pem1_pdu_unit = 0, pem1_pdu_slot = 0 WHERE pem1_pdu_id = '{0}'".format(id))
  db.do("DELETE FROM pdus WHERE id = '{0}'".format(id))
 return { 'res':'op_success' }

#
# Update PDU slot info for a device
#
def update_device_pdus(aDict):
 from sdcp import PackageContainer as PC
 PC.log_msg("pdu_update_device_pdus({})".format(aDict))
 from sdcp.core.dbase import DB
 hostname  = aDict.get('hostname')
 ret = {}
 with DB() as db:
  for p in ['0','1']:
   ret[p] = None
   id = aDict.get("pem{}_pdu_id".format(p))
   if id:
    slot = int(aDict.get("pem{}_pdu_slot".format(p),0))
    unit = int(aDict.get("pem{}_pdu_unit".format(p),0))
    if not (slot == 0 or unit == 0):
     from sdcp.devices.avocent import Device
     db.do("SELECT INET_NTOA(ip) as ip FROM pdus WHERE id = '{}'".format(id))
     pdu = db.get_row()
     avocent = Device(pdu['ip'])
     ret["pem{}".format(p)] = avocent.set_name(slot,unit,hostname+"-P{}".format(p))
 return ret
