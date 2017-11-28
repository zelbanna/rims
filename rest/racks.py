"""Module docstring.

Tools REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

#
#
def infra(aDict):
 from sdcp.core.dbase import DB
 ret =  {'res':'OK' }
 with DB() as db:
  ret['typexist'] = db.do("SELECT id, name, base FROM devicetypes") 
  ret['types']    = db.get_rows()
  ret['rackxist'] = db.do("SELECT racks.* FROM racks")
  ret['racks']    = db.get_rows()
  ret['racks'].append({ 'id':'NULL', 'name':'Not used'})
  ret['consolexist'] = db.do("SELECT id, name, INET_NTOA(ip) as ipasc FROM consoles") 
  ret['consoles']    = db.get_rows()
  ret['consoles'].append({ 'id':'NULL', 'name':'No Console', 'ip':2130706433, 'ipasc':'127.0.0.1' })
  ret['pduxist'] = db.do("SELECT pdus.*, INET_NTOA(ip) as ipasc FROM pdus")
  ret['pdus']    = db.get_rows()
  ret['pdus'].append({ 'id':'NULL', 'name':'No PDU', 'ip':'127.0.0.1', 'slots':0, '0_slot_id':0, '0_slot_name':'', '1_slot_id':0, '1_slot_name':'' })
  ret['dnscachexist'] = db.do("SELECT domains.* FROM domains")
  ret['dnscache']     = db.get_rows()
 return ret

#
# rackinf([id:<rackid>])
def rackinfo(aDict):
 from sdcp.core.dbase import DB
 ret  =  {'res':'OK'}
 with DB() as db:
  if aDict.get('id'):
   data = {'name': None, 'console':[], 'pdu':[] }
   res = db.do("SELECT racks.name, fk_pdu_1 AS pdu_1, fk_pdu_2 AS pdu_2, fk_console AS console_1 FROM racks WHERE racks.id=%s"%aDict['id'])
   try:
    select = db.get_row()
    data['name'] = select.pop('name',"Noname")
    if select.get('pdu_1') == select.get('pdu_2'):
     select.pop('pdu_2',None)
    for type_no,value in select.iteritems():
     type,void,no = type_no.partition('_')
     if value:
      db.do("SELECT id, name, INET_NTOA(ip) AS ipasc FROM %ss WHERE id = %i"%(type,value))
      data[type].append(db.get_row())
   except: pass
  else:
   data = {}
   for type in ['pdu','console']:
    res = db.do("SELECT id, name, INET_NTOA(ip) AS ipasc FROM %ss"%type)
    data[type] = db.get_rows()
 ret['data'] = data
 return ret

