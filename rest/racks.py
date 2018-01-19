"""Module docstring.

Tools REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

from ..core.dbase import DB

#
# info([id:<rackid>])
def info(aDict):
 ret  =  {}
 with DB() as db:
  if aDict.get('id'):
   data = {'name': None, 'console':[], 'pdu':[] }
   res = db.do("SELECT name, pdu_1, pdu_2, console FROM racks WHERE id = %s"%aDict['id'])
   try:
    select = db.get_row()
    data['name'] = select.pop('name',"Noname")
    if select.get('console'):
     value = select.pop('console',None)
     db.do("SELECT devices.id, devices.hostname, INET_NTOA(ip) AS ipasc, devicetypes.name AS type FROM devices INNER JOIN devicetypes ON devices.type_id = devicetypes.id WHERE devices.id = %i"%value)
     data['console'].append(db.get_row())

    if select.get('pdu_1') == select.get('pdu_2'):
     select.pop('pdu_2',None)
    for pdu_no,value in select.iteritems():
     if value:
      db.do("SELECT id, name AS hostname, INET_NTOA(ip) AS ipasc, 'pdu' AS type FROM pdus WHERE id = %i"%value)
      data['pdu'].append(db.get_row())

   except: pass
  else:
   data = {}
   db.do("SELECT devices.id, devices.hostname, INET_NTOA(ip) AS ipasc, devicetypes.name AS type FROM devices INNER JOIN devicetypes ON devices.type_id = devicetypes.id WHERE devicetypes.base = 'console'")
   data['console'] = db.get_rows()
   res = db.do("SELECT id, name AS hostname, INET_NTOA(ip) AS ipasc, 'pdu' AS type FROM pdus")
   data['pdu'] = db.get_rows()

 ret['data'] = data
 from ..core.logger import log
 log(data)
 return ret

#
#
def infra(aDict):
 ret =  {}
 with DB() as db:
  ret['typexist'] = db.do("SELECT id, name, base FROM devicetypes") 
  ret['types']    = db.get_rows()
  ret['rackxist'] = db.do("SELECT racks.* FROM racks")
  ret['racks']    = db.get_rows()
  ret['racks'].append({ 'id':'NULL', 'name':'Not used'})
  ret['consolexist'] = db.do("SELECT devices.id, devices.hostname AS name, ip, INET_NTOA(ip) AS ipasc, devicetypes.name AS type FROM devices INNER JOIN devicetypes ON devices.type_id = devicetypes.id WHERE devicetypes.base = 'console'") 
  ret['consoles']    = db.get_rows()
  ret['consoles'].append({ 'id':'NULL', 'name':'No Console', 'ip':2130706433, 'ipasc':'127.0.0.1' })
  ret['pduxist'] = db.do("SELECT pdus.*, INET_NTOA(ip) as ipasc FROM pdus")
  ret['pdus']    = db.get_rows()
  ret['pdus'].append({ 'id':'NULL', 'name':'No PDU', 'ip':'127.0.0.1', 'slots':0, '0_slot_id':0, '0_slot_name':'', '1_slot_id':0, '1_slot_name':'' })
  ret['dnscachexist'] = db.do("SELECT domains.* FROM domains")
  ret['dnscache']     = db.get_rows()
 return ret

#
# devices(rack:rack_id, sort:)
#
def devices(aDict):
 ret = {'sort':aDict.get('sort','devices.id')}
 tune = "INNER JOIN rackinfo ON rackinfo.device_id = devices.id WHERE rackinfo.rack_id = '{}'".format(aDict['rack'])
 if aDict.get('filter'):
  tune += " AND type_id = {}".format(aDict['filter'])

 with DB() as db:
  sql = "SELECT devices.id, INET_NTOA(ip) as ipasc, hostname, domains.name as domain, model, type_id, subnets.gateway FROM devices JOIN subnets ON subnet_id = subnets.id JOIN domains ON domains.id = devices.a_dom_id {0} ORDER BY {1}".format(tune,ret['sort'])
  ret['xist'] = db.do(sql)
  ret['data']= db.get_rows()
 return ret
