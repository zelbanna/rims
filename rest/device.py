"""Module docstring.

 Device restAPI module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

from sdcp.core.dbase import DB
from sdcp.core.logger import log

#
# update(id,**key:value pairs)
#
def update(aDict):
 log("device_update({})".format(aDict))
 from sdcp.core import genlib as GL
 id     = aDict.pop('id',None)
 racked = aDict.pop('racked',None)
 ret    = {'res':'OK'}
 with DB() as db:
  if racked:
   if   racked == '0' and aDict.get('rackinfo_rack_id') != 'NULL':
    db.do("INSERT INTO rackinfo SET device_id = {},rack_id={} ON DUPLICATE KEY UPDATE rack_id = rack_id".format(id,aDict['rackinfo_rack_id']))
   elif racked == '1' and aDict.get('rackinfo_rack_id') == 'NULL':
    db.do("DELETE FROM rackinfo WHERE device_id = {}".format(id))

  tbl_id = { 'devices':'id', 'rackinfo':'device_id' } 
  for fkey in aDict.keys():
   change = 0
   # fkey = table _ key
   (table, void, key) = fkey.partition('_')
   data = aDict.get(fkey)
   if not (key[0:3] == 'pem' and key[5:] == 'pdu_slot_id'):
    if key == 'mac':
     data = GL.mac2int(data)
    sql = "UPDATE " + table + " SET {0}=" + ("'{3}'" if data != 'NULL' else "NULL") + " WHERE {1} = '{2}'"
    change = db.do(sql.format(key,tbl_id[table],id,data))
   else:
    pem = key[:4]
    [pemid,pemslot] = data.split('.')
    change = db.do("UPDATE rackinfo SET {0}_pdu_id={1}, {0}_pdu_slot ='{2}' WHERE device_id = '{3}'".format(pem,pemid,pemslot,id))
   if change > 0:
    ret[key] = 'CHANGED'
 return ret

#
# new(ip, hostname, ipam_sub_id, a_dom_id, mac, target, arg)
#
def new(aDict):
 log("device_new({})".format(aDict))
 from sdcp.core import genlib as GL
 ip    = aDict.get('ip')
 ipint = GL.ip2int(ip)
 ipam_sub_id = aDict.get('ipam_sub_id')
 ret = {'res':'NOT_OK', 'info':None}
 with DB() as db:
  in_sub = db.do("SELECT subnet FROM subnets WHERE id = {0} AND {1} > subnet AND {1} < (subnet + POW(2,(32-mask))-1)".format(ipam_sub_id,ipint))
  if in_sub == 0:
   ret['info'] = "IP not in subnet range"
  elif aDict.get('hostname') == 'unknown':
   ret['info'] = "Hostname unknown not allowed"
  else:
   xist = db.do("SELECT id, hostname, INET_NTOA(ip) AS ipasc, a_dom_id, ptr_dom_id FROM devices WHERE ipam_sub_id = {} AND (ip = {} OR hostname = '{}')".format(ipam_sub_id,ipint,aDict.get('hostname')))
   if xist == 0:
    res = db.do("SELECT id FROM domains WHERE name = '{}'".format(GL.ip2arpa(ip)))
    ptr_dom_id = db.get_val('id') if res > 0 else 'NULL'
    mac = GL.mac2int(aDict.get('mac',0))
    ret['insert'] = db.do("INSERT INTO devices (ip,vm,mac,a_dom_id,ptr_dom_id,ipam_sub_id,ipam_id,hostname,fqdn,snmp,model,type) VALUES({},{},{},{},{},{},{},'{}','{}','unknown','unknown','unknown')".format(ipint,aDict.get('vm'),mac,aDict['a_dom_id'],ptr_dom_id,ipam_sub_id,aDict.get('ipam_id','0'),aDict['hostname'],aDict['fqdn']))
    ret['id']   = db.get_last_id()
    if aDict.get('target') == 'rack_id' and aDict.get('arg'):
     db.do("INSERT INTO rackinfo SET device_id = {}, rack_id = {} ON DUPLICATE KEY UPDATE rack_unit = 0, rack_size = 1".format(ret['id'],aDict.get('arg')))
     ret['rack'] = aDict.get('arg')
     ret['info'] = "rack"
    ret['res']  = "OK"
   else:
    ret['info']  = "existing"
    ret.update(db.get_row())
 return ret

#
# discover(start, end, clear, a_dom_id, ipam_sub_id)
#
# - subnet can cross ptr_dom_id so need to deduce per ip..
#
def discover(aDict):
 log("device_discover({})".format(aDict))
 from time import time
 from threading import Thread, BoundedSemaphore
 from sdcp.core import genlib as GL
 start_time = int(time())
 ip_start = aDict.get('start')
 ip_end   = aDict.get('end')
 ret = { 'res':'OK', 'errors':0 }

 def _tdetect(aip,adict,asema,atypes):
  res = detect({'ip':aip,'types':atypes})
  if res['res'] == 'OK':
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
   sql = "INSERT INTO devices (ip, a_dom_id, ptr_dom_id, ipam_sub_id, hostname, snmp, model, type_id, fqdn) VALUES ({},"+aDict['a_dom_id']+",{},{},'{}','{}','{}','{}','{}')"
   db.do("SELECT id,name FROM domains WHERE name LIKE '%arpa%'")
   ptr_doms = db.get_dict('name')
   for ip,entry in db_new.iteritems():
    log("device_discover - adding:{}->{}".format(ip,entry))
    ptr_dom_id = ptr_doms.get(GL.ip2arpa(ip),{ 'id':'NULL' })['id']
    db.do(sql.format(GL.ip2int(ip), ptr_dom_id, aDict.get('ipam_sub_id'), entry['name'],entry['snmp'],entry['model'],entry['type_id'],entry['fqdn']))
  except Exception as err:
   log("device discover: Error [{}]".format(str(err)))
   ret['res']    = 'NOT_OK'
   ret['info']   = "Error:{}".format(str(err))
   ret['errors'] = ret['errors'] + 1

  ret['info'] = "Time spent:{}".format(int(time()) - start_time)
  ret['found']= len(db_new)
 return ret

#
def detect(aDict):
 log("device_detect({})".format(aDict))
 from sdcp import PackageContainer as PC
 from netsnmp import VarList, Varbind, Session
 from socket import gethostbyaddr
 from os import system
 if system("ping -c 1 -w 1 {} > /dev/null 2>&1".format(aDict['ip'])) != 0:
  return {'res':'NOT_OK'}

 try:
  # .1.3.6.1.2.1.1.1.0 : Device info
  # .1.3.6.1.2.1.1.5.0 : Device name
  devobjs = VarList(Varbind('.1.3.6.1.2.1.1.1.0'), Varbind('.1.3.6.1.2.1.1.5.0'))
  session = Session(Version = 2, DestHost = aDict['ip'], Community = PC.snmp['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
  session.get(devobjs)
 except:
  pass

 info = {'fqdn':'unknown','name':'unknown','model':'unknown', 'type_name':'generic'}
 info['snmp'] = devobjs[1].val.lower() if devobjs[1].val else 'unknown'
 try:
  info['fqdn'] = gethostbyaddr(aDict['ip'])[0]
  info['name'] = info['fqdn'].partition('.')[0].lower()
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
    update = db.do("UPDATE devices SET snmp = '{}', fqdn = '{}', model = '{}', type_id = '{}' WHERE id = '{}'".format(info['snmp'],info['fqdn'],info['model'],info['type_id'],aDict['id'])) > 0
 return { 'res':'OK', 'update':update, 'info':info}

#
# remove(id) and pop dns and ipam info
#
def remove(aDict):
 log("device_remove({})".format(aDict))
 with DB() as db:
  xist = db.do("SELECT hostname, mac, a_id, ptr_id, ipam_id FROM devices WHERE id = {}".format(aDict.get('id','0')))
  if xist == 0:
   ret = { 'res':'NOT_OK', 'a_id':0, 'ptr_id':0, 'ipam_id':0 }
  else:
   ret = db.get_row()
   ret['deleted'] = db.do("DELETE FROM devices WHERE id = '{}'".format(aDict['id']))
   ret['res'] = 'OK'
 return ret

#
# dump(columns)
# - columns is a string list
#
def dump_db(aDict):
 cols = aDict.get('columns','*')
 tbl  = aDict.get('table','devices')
 ret  = {'res':'OK'} 
 with DB() as db:
  ret['found'] = db.do("SELECT {} FROM {}".format(cols,tbl))
  ret['db'] = db.get_rows() if ret['found'] > 0 else []
 return ret

#
# find_ip(ipam_sub_id, consecutive)
#
# - Find X consecutive ip from a particular subnet-id
# ipam_sub_id: X
# consecutive: X

def find_ip(aDict):
 log("device_find_ip({})".format(aDict))
 from sdcp.core import genlib as GL
 sub_id = aDict.get('ipam_sub_id')
 with DB() as db:
  db.do("SELECT subnet, INET_NTOA(subnet) as subasc, mask FROM subnets WHERE id = {}".format(sub_id))
  sub = db.get_row()
  db.do("SELECT ip FROM devices WHERE ipam_sub_id = {}".format(sub_id))
  iplist = db.get_dict('ip')
 subnet = int(sub.get('subnet'))
 start  = None
 ret    = { 'subnet':sub['subasc'], 'res':'NOT_OK' }
 for ip in range(subnet + 1, subnet + 2**(32-int(sub.get('mask')))-1):
  if iplist.get(ip):
   start = None
  elif not start:
   count = int(aDict.get('consecutive',1))
   if count > 1:
    start = ip
   else:
    ret['ip'] = GL.int2ip(ip)
    ret['res'] = 'OK'
    break
  else:
   if count == 2:
    ret['start'] = GL.int2ip(start)
    ret['end'] = GL.int2ip(start+int(aDict.get('consecutive'))-1)
    ret['res'] = 'OK'
    break
   else:
    count = count - 1
 return ret

#
# info(id)
#
def info(aDict):
 log("device_info({})".format(aDict))
 ret = {}
 search = "devices.id = {}".format(aDict['id']) if aDict.get('id') else "devices.ip = INET_ATON('{}')".format(aDict.get('ip'))
 with DB() as db:
  ret['exist'] = db.do("SELECT devices.*, devicetypes.base as type_base, devicetypes.name as type_name, subnets.subnet, a.name as a_name, INET_NTOA(ip) as ipasc FROM devices LEFT JOIN domains AS a ON devices.a_dom_id = a.id JOIN subnets ON devices.ipam_sub_id = subnets.id LEFT JOIN devicetypes ON devicetypes.id = devices.type_id WHERE {}".format(search))
  if ret['exist'] > 0:
   ret['info'] = db.get_row()
   ret['fqdn'] = "{}.{}".format(ret['info']['hostname'],ret['info']['a_name'])
   ret['ip']   = ret['info']['ipasc']
   ret['type'] = ret['info']['type_base']
   ret['res']  = 'OK'
   ret['booked'] = db.do("SELECT users.alias, bookings.user_id, NOW() < ADDTIME(time_start, '30 0:0:0.0') AS valid FROM bookings LEFT JOIN users ON bookings.user_id = users.id WHERE device_id ='{}'".format(ret['info']['id']))
   if ret['booked'] > 0:
    ret['booking'] = db.get_row()
   if ret['info']['vm'] == 1:
    ret['racked'] = 0
   else:
    ret['racked'] = db.do("SELECT rackinfo.*, INET_NTOA(consoles.ip) AS console_ip, consoles.name AS console_name FROM rackinfo LEFT JOIN consoles ON consoles.id = rackinfo.console_id WHERE rackinfo.device_id = {}".format(ret['info']['id']))
    if ret['racked'] > 0:
     ret['rack'] = db.get_row()
     ret['rack']['hostname'] = ret['info']['hostname']
  else:
   ret['res'] = 'NOT_OK'
 return ret
