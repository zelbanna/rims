"""Moduledocstring.

PDU REST calls module
- should be renamed avocentpdu and device handling should use proper type based REST calls

"""
__author__= "Zacharias El Banna"                     
__version__ = "17.11.01GA"
__status__= "Production"

#
# Update PDU slot info (name basically)
#
def update(aDict):
 if aDict.get('name'):
  from ..devices.avocent import Device
  name = aDict.get('name')
  ip   = aDict.get('pdu')
  slot = aDict.get('slot','0')
  unit = aDict.get('unit','0')
  avocent = Device(ip)
  res = avocent.set_name(slot,unit,name)
  return { 'info':res }
 else:
  return { 'info':'No name supplied' }

#
# Update PDU slot info for a device
#
def update_device(aDict):
 from ..core.dbase import DB
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
     from ..devices.avocent import Device
     db.do("SELECT INET_NTOA(ip) as ip FROM devices WHERE id = '{}'".format(id))
     avocent = Device(db.get_val('ip'))
     ret["pem{}".format(p)] = avocent.set_name(slot,unit,hostname+"-P{}".format(p))
 return ret
