"""Module docstring.

 Device API module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

from sdcp.core.dbase import DB
from sdcp.core.logger import log

#
#
def info(aDict):
 """
 Takes id or ascii rep of ip and return info
 """
 ret = {}
 search = "devices.id = '{}'".format(aDict['id']) if aDict.get('id') else "devices.ip = INET_ATON('{}')".format(aDict.get('ip'))
 with DB() as db:
  ret['exist'] = db.do("SELECT devices.*, devicetypes.base as type_base, devicetypes.name as type_name, a.name as domain, INET_NTOA(ip) as ipasc, CONCAT(INET_NTOA(subnets.subnet),'/',subnets.mask) AS subnet, INET_NTOA(subnets.gateway) AS gateway FROM devices LEFT JOIN domains AS a ON devices.a_dom_id = a.id LEFT JOIN devicetypes ON devicetypes.id = devices.type_id LEFT JOIN subnets ON subnets.id = subnet_id WHERE {}".format(search))
  if ret['exist'] > 0:
   ret['info'] = db.get_row()
   ret['fqdn'] = "{}.{}".format(ret['info']['hostname'],ret['info']['domain'])
   ret['ip']   = ret['info'].pop('ipasc',None)
   ret['type'] = ret['info']['type_base']
   ret['mac']  = ':'.join(s.encode('hex') for s in str(hex(ret['info']['mac']))[2:].zfill(12).decode('hex')).lower() if ret['info']['mac'] != 0 else "00:00:00:00:00:00"
   ret['result']  = 'OK'
   ret['id']   = ret['info'].pop('id',None)
   ret['booked'] = db.do("SELECT users.alias, bookings.user_id, NOW() < ADDTIME(time_start, '30 0:0:0.0') AS valid FROM bookings LEFT JOIN users ON bookings.user_id = users.id WHERE device_id ='{}'".format(ret['id']))
   if ret['booked'] > 0:
    ret['booking'] = db.get_row()
   if ret['info']['vm'] == 1:
    ret['racked'] = 0
   else:
    ret['racked'] = db.do("SELECT rackinfo.*, INET_NTOA(consoles.ip) AS console_ip, consoles.name AS console_name FROM rackinfo LEFT JOIN consoles ON consoles.id = rackinfo.console_id WHERE rackinfo.device_id = {}".format(ret['id']))
    if ret['racked'] > 0:
     ret['rack'] = db.get_row()
     ret['rack']['hostname'] = ret['info']['hostname']
  else:
   ret['result'] = 'NOT_OK'
 return ret

#
#
def update(aDict):
 """
 Update device info
  - id
  - **table_key:value pairs, table: devices/rackinfo
 """
 log("device_update({})".format(aDict))
 from sdcp.core import genlib as GL
 id     = aDict.pop('id',None)
 racked = aDict.pop('racked',None)
 ret    = {'result':'OK', 'data':{}}
 with DB() as db:
  # specials
  try: aDict['devices_mac'] = GL.mac2int(aDict.pop('devices_mac','00:00:00:00:00:00'))
  except: pass

  if racked:
   if   racked == '1' and aDict.get('rackinfo_rack_id') == 'NULL':
    db.do("DELETE FROM rackinfo WHERE device_id = {}".format(id))
    aDict.pop('rackinfo_pem0_pdu_slot_id',None)
    aDict.pop('rackinfo_pem1_pdu_slot_id',None)
   elif racked == '0' and aDict.get('rackinfo_rack_id') != 'NULL':
    db.do("INSERT INTO rackinfo SET device_id = {},rack_id={} ON DUPLICATE KEY UPDATE rack_id = rack_id".format(id,aDict['rackinfo_rack_id']))
   elif racked == '1':
    for pem in ['pem0','pem1']:
     try:
      pem_pdu_slot_id = aDict.pop('rackinfo_%s_pdu_slot_id'%pem,None)
      (aDict['rackinfo_%s_pdu_id'%pem],aDict['rackinfo_%s_pdu_slot'%pem]) = pem_pdu_slot_id.split('.')
     except: pass

  tbl_id = { 'devices':'id', 'rackinfo':'device_id' }
  sql    = "UPDATE %s SET %s=%s WHERE %s = '%s'"
  for tkey in aDict.keys():
   (table, void, key) = tkey.partition('_')
   data = aDict[tkey]
   if db.do(sql%(table,key,"'%s'"%data if data != 'NULL' else "NULL",tbl_id[table],id)) > 0:
    ret['data'][key] = 'CHANGED'
 return ret

#
#
def new(aDict):
 """
 new(ip, hostname, subnet_id, a_dom_id, mac, target, arg)
 - target is 'rack_id' or nothing
 - arg is rack_id
 """
 log("device_new({})".format(aDict))
 from sdcp.core import genlib as GL
 ip    = aDict.get('ip')
 ipint = GL.ip2int(ip)
 subnet_id = aDict.get('subnet_id')
 ret = {'result':'NOT_OK', 'info':None}
 with DB() as db:
  in_sub = db.do("SELECT subnet FROM subnets WHERE id = {0} AND {1} > subnet AND {1} < (subnet + POW(2,(32-mask))-1)".format(subnet_id,ipint))
  if in_sub == 0:
   ret['info'] = "IP not in subnet range"
  elif aDict.get('hostname') == 'unknown':
   ret['info'] = "Hostname unknown not allowed"
  else:
   xist = db.do("SELECT id, hostname, INET_NTOA(ip) AS ipasc, a_dom_id FROM devices WHERE subnet_id = {} AND (ip = {} OR hostname = '{}')".format(subnet_id,ipint,aDict.get('hostname')))
   if xist == 0:
    mac = GL.mac2int(aDict.get('mac',0))
    ret['insert'] = db.do("INSERT INTO devices (ip,vm,mac,a_dom_id,subnet_id,hostname,lookup,snmp,model) VALUES({},{},{},{},{},'{}','unknown','unknown','unknown')".format(ipint,aDict.get('vm'),mac,aDict['a_dom_id'],subnet_id,aDict['hostname']))
    ret['id']   = db.get_last_id()
    if aDict.get('target') == 'rack_id' and aDict.get('arg'):
     db.do("INSERT INTO rackinfo SET device_id = {}, rack_id = {} ON DUPLICATE KEY UPDATE rack_unit = 0, rack_size = 1".format(ret['id'],aDict.get('arg')))
     ret['rack'] = aDict.get('arg')
     ret['info'] = "rack"
    ret['result']  = "OK"
   else:
    ret['info']  = "existing"
    ret.update(db.get_row())
 return ret

#
# remove(id) and pop dns and ipam info
#
def remove(aDict):
 log("device_remove({})".format(aDict))
 with DB() as db:
  xist = db.do("SELECT hostname, mac, a_id, ptr_id FROM devices WHERE id = {}".format(aDict.get('id','0')))
  if xist == 0:
   ret = { 'result':'NOT_OK', 'a_id':0, 'ptr_id':0 }
  else:
   ret = db.get_row()
   ret['deleted'] = db.do("DELETE FROM devices WHERE id = '{}'".format(aDict['id']))
   ret['result'] = 'OK'
 return ret

#
# discover(start, end, clear, a_dom_id, subnet_id)
#
def discover(aDict):
 log("device_discover({})".format(aDict))
 from time import time
 from threading import Thread, BoundedSemaphore
 from sdcp.core import genlib as GL
 start_time = int(time())
 ip_start = aDict.get('start')
 ip_end   = aDict.get('end')
 ret = { 'result':'OK', 'errors':0 }

 def _tdetect(aip,adict,asema,atypes):
  res = detect({'ip':aip,'types':atypes})
  if res['result'] == 'OK':
   adict[aip] = res['info']
  asema.release()
  return True

 with DB() as db:

  db.do("SELECT id,name FROM devicetypes")
  devtypes = db.get_dict('name')

  db_old, db_new = {}, {}
  if aDict.get('clear',False):
   db.do("TRUNCATE TABLE devices")
  else:
   db.do("SELECT ip FROM devices WHERE ip >= {} and ip <= {}".format(ip_start,ip_end))
   rows = db.get_rows()
   for item in rows:
    db_old[item.get('ip')] = True
  try:
   sema = BoundedSemaphore(10)
   for ip in GL.ipint2range(ip_start,ip_end):
    if db_old.get(GL.ip2int(ip),None):
     continue
    sema.acquire()
    t = Thread(target = _tdetect, args=[ip, db_new, sema, devtypes])
    t.name = "Detect " + ip
    t.start()

   # Join all threads by acquiring all semaphore resources
   for i in range(10):
    sema.acquire()
   # We can now do inserts only (no update) as either we clear or we skip existing :-)
   sql = "INSERT INTO devices (ip, a_dom_id, subnet_id, hostname, snmp, model, type_id, lookup) VALUES ({},"+aDict['a_dom_id']+",{},'{}','{}','{}','{}','{}')"
   for ip,entry in db_new.iteritems():
    log("device_discover - adding:{}->{}".format(ip,entry))
    db.do(sql.format(GL.ip2int(ip), aDict.get('subnet_id'), entry['name'],entry['snmp'],entry['model'],entry['type_id'],entry['lookup']))
  except Exception as err:
   log("device discover: Error [{}]".format(str(err)))
   ret['result']    = 'NOT_OK'
   ret['info']   = "Error:{}".format(str(err))
   ret['errors'] += 1

  ret['info'] = "Time spent:{}".format(int(time()) - start_time)
  ret['found']= len(db_new)
 return ret


#
#
#
def detect(aDict):
 log("device_detect({})".format(aDict))
 from sdcp import PackageContainer as PC
 from netsnmp import VarList, Varbind, Session
 from socket import gethostbyaddr
 from os import system
 if system("ping -c 1 -w 1 {} > /dev/null 2>&1".format(aDict['ip'])) != 0:
  return {'result':'NOT_OK'}

 try:
  # .1.3.6.1.2.1.1.1.0 : Device info
  # .1.3.6.1.2.1.1.5.0 : Device name
  devobjs = VarList(Varbind('.1.3.6.1.2.1.1.1.0'), Varbind('.1.3.6.1.2.1.1.5.0'))
  session = Session(Version = 2, DestHost = aDict['ip'], Community = PC.snmp['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
  session.get(devobjs)
 except:
  pass

 info = {'lookup':'unknown','name':'unknown','model':'unknown', 'type_name':'generic'}
 info['snmp'] = devobjs[1].val.lower() if devobjs[1].val else 'unknown'
 try:
  info['lookup'] = gethostbyaddr(aDict['ip'])[0]
  info['name'] = info['lookup'].partition('.')[0].lower()
 except:
  pass

 if devobjs[0].val:
  infolist = devobjs[0].val.split()
  if infolist[0] == "Juniper":
   if infolist[1] == "Networks,":
    info['model'] = infolist[3].lower()
    for tp in [ 'ex', 'srx', 'qfx', 'mx', 'wlc' ]:
     if tp in info['model']:
      info['type_name'] = tp
      break
   else:
    subinfolist = infolist[1].split(",")
    info['model'] = subinfolist[2]
  elif infolist[0] == "VMware":
   info['model'] = "esxi"
   info['type_name']  = "esxi"
  elif infolist[0] == "Linux":
   info['model'] = 'debian' if "Debian" in devobjs[0].val else 'generic'
  else:
   info['model'] = " ".join(infolist[0:4])

 update = aDict.get('update',False)
 if aDict.get('types') and not update:
  info['type_id'] = aDict['types'][info['type_name']]['id']
 else:
  from sdcp.core.dbase import DB
  with DB() as db:
   xist = db.do("SELECT id,name FROM devicetypes WHERE name = '{}'".format(info['type_name']))
   info['type_id'] = db.get_val('id') if xist > 0 else None
   if update:
    update = db.do("UPDATE devices SET snmp = '{}', lookup = '{}', model = '{}', type_id = '{}' WHERE id = '{}'".format(info['snmp'],info['lookup'],info['model'],info['type_id'],aDict['id'])) > 0
 return { 'result':'OK', 'update':update, 'info':info}

#
# list(rack:[rack_id,vm], sort:)
#
def list(aDict):
 ret = { 'result':'OK' }
 if aDict.get('rack'):
  if aDict['rack'] == 'vm':
   tune = "WHERE vm = 1"
  else:
   tune = "INNER JOIN rackinfo ON rackinfo.device_id = devices.id WHERE rackinfo.rack_id = '{}'".format(aDict['rack'])
  if aDict.get('filter'):
   tune += " AND type_id = {}".format(aDict['filter'])
 elif aDict.get('filter'):
  tune = "WHERE type_id = {}".format(aDict['filter'])
 else:
  tune = ""

 ret = {'result':'OK','sort':aDict.get('sort','devices.id')}
 with DB() as db:
  sql = "SELECT devices.id, INET_NTOA(ip) as ipasc, hostname, domains.name as domain, model, type_id, subnets.gateway FROM devices JOIN subnets ON subnet_id = subnets.id JOIN domains ON domains.id = devices.a_dom_id {0} ORDER BY {1}".format(tune,ret['sort'])
  ret['xist'] = db.do(sql)
  ret['data']= db.get_rows()
 return ret
 
#
#
def list_type(aDict):
 ret = { 'result':'OK' }
 with DB() as db:
  select = "devicetypes.%s ='%s'"%(('name',aDict.get('name')) if aDict.get('name') else ('base',aDict.get('base')))
  ret['xist'] = db.do("SELECT devices.id, INET_NTOA(ip) AS ipasc, hostname, devicetypes.base as type_base, devicetypes.name as type_name FROM devices LEFT JOIN devicetypes ON devices.type_id = devicetypes.id WHERE %s ORDER BY type_name,hostname"%select)
  ret['data'] = db.get_rows() 
 return ret
#
#
def clear(aDict):
 ret = { 'result':'OK' }
 with DB() as db:
  db.do("TRUNCATE TABLE devices")
 return ret

