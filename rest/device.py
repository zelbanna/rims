"""Module docstring.

 Device restAPI module

"""
__author__ = "Zacharias El Banna"                     
__version__ = "17.10.4"
__status__ = "Production"

from sdcp.core.dbase import DB
import sdcp.PackageContainer as PC

#
# update(id,**key:value pairs)
#
def update(aDict):
 PC.log_msg("device_update({})".format(aDict))
 import sdcp.core.genlib as GL
 id     = aDict.pop('id',None)
 racked = aDict.pop('racked',None)
 with DB() as db:
  if racked:
   if racked == '0' and aDict.get('rackinfo_rack_id') != 'NULL':
    db.do("INSERT INTO rackinfo SET device_id = {},rack_id={} ON DUPLICATE KEY UPDATE rack_unit = 0, rack_size = 1".format(id,aDict.get('rackinfo_rack_id')))
    db.commit()
   elif racked == '1' and aDict.get('rackinfo_rack_id') == 'NULL':
    db.do("DELETE FROM rackinfo WHERE device_id = {}".format(id))
    db.commit()

  tbl_id = { 'devices':'id', 'rackinfo':'device_id' } 
  for fkey in aDict.keys():
   # fkey = table _ key
   (table, void, key) = fkey.partition('_')
   data = aDict.get(fkey)
   if key == 'mac' and GL.is_mac(data):
    mac = GL.mac2int(data)
    db.do("UPDATE {0} SET mac='{1}' WHERE {2} = '{3}'".format(table,mac,tbl_id[table],id))
   elif not (key[0:3] == 'pem' and key[5:] == 'pdu_slot_id'):
    if data == 'NULL':
     db.do("UPDATE {0} SET {1}=NULL WHERE {2} = '{3}'".format(table,key,tbl_id[table],id))
    else:
     db.do("UPDATE {0} SET {1}='{4}' WHERE {2} = '{3}'".format(table,key,tbl_id[table],id,data))
   else:
    pem = key[:4]
    [pemid,pemslot] = data.split('.')
    db.do("UPDATE rackinfo SET {0}_pdu_id={1}, {0}_pdu_slot ='{2}' WHERE device_id = '{3}'".format(pem,pemid,pemslot,id))
  db.commit()
 return { 'res':'update','keys':aDict.keys() }

#
# new(ip, hostname, ipam_sub_id, a_dom_id, mac, target, arg)
#
def new(aDict):
 PC.log_msg("device_new({})".format(aDict))
 import sdcp.core.genlib as GL
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
    ptr_dom_id = db.get_row().get('id') if res > 0 else 'NULL'
    mac = 0 if not GL.is_mac(aDict.get('mac',False)) else GL.mac2int(aDict['mac'])
    ret['insert'] = db.do("INSERT INTO devices (ip,vm,mac,a_dom_id,ptr_dom_id,ipam_sub_id,ipam_id,hostname,fqdn,snmp,model,type) VALUES({},{},{},{},{},{},{},'{}','{}','unknown','unknown','unknown')".format(ipint,aDict.get('vm'),mac,aDict['a_dom_id'],ptr_dom_id,ipam_sub_id,aDict.get('ipam_id','0'),aDict['hostname'],aDict['fqdn']))
    ret['id']   = db.get_last_id()
    if aDict.get('target') == 'rack_id' and aDict.get('arg'):
     db.do("INSERT INTO rackinfo SET device_id = {}, rack_id = {} ON DUPLICATE KEY UPDATE rack_unit = 0, rack_size = 1".format(ret['id'],aDict.get('arg')))
     ret['rack'] = aDict.get('arg')
     ret['info'] = "rack"
    db.commit()
    ret['res']  = "OK"
   else:
    ret['info']  = "existing"
    ret.update(db.get_row())
 return ret

#
# discover(start, end, clear, a_dom_id, ipam_sub_id)
#
def discover(aDict):
 PC.log_msg("device_discover({})".format(aDict))
 from time import time
 from threading import Thread, BoundedSemaphore
 from sdcp.devices.DevHandler import device_detect
 import sdcp.core.genlib as GL
 start_time = int(time())
 ip_start = aDict.get('start')
 ip_end   = aDict.get('end')
 with DB() as db:
  db_old, db_new = {}, {}
  if aDict.get('clear',False):
   db.do("TRUNCATE TABLE devices")
   db.commit()
  else:
   res  = db.do("SELECT ip FROM devices WHERE ip >= {} and ip <= {}".format(ip_start,ip_end))
   rows = db.get_rows()
   for item in rows:
    db_old[item.get('ip')] = True
  try:
   sema = BoundedSemaphore(10)
   for ip in GL.ipint2range(ip_start,ip_end):
    if db_old.get(GL.ip2int(ip),None):
     continue
    sema.acquire()
    t = Thread(target = device_detect, args=[ip, db_new, sema])
    t.name = "Detect " + ip
    t.start()
  
   # Join all threads by acquiring all semaphore resources
   for i in range(10):
    sema.acquire()
   # We can do insert only (no update) as either we clear or we skip existing :-)
   sql = "INSERT INTO devices (ip, a_dom_id, ptr_dom_id, ipam_sub_id, hostname, snmp, model, type, fqdn) VALUES ({0},{1},{2},{3},'{4}','{5}','{6}','{7}','{8}')"
   res = db.do("SELECT id,name FROM domains WHERE name LIKE '%arpa%'")
   ptr_doms = db.get_rows_dict('name')
   for ip,entry in db_new.iteritems():
    ptr_dom_id = ptr_doms.get(GL.ip2arpa(ip),{ 'id':'NULL' })['id']
    db.do(sql.format(GL.ip2int(ip), aDict.get('a_dom_id'), ptr_dom_id, aDict.get('ipam_sub_id'), entry['hostname'],entry['snmp'],entry['model'],entry['type'],entry['fqdn']))
   else:
    db.commit()
  except Exception as err:
   PC.log_msg("device discover: Error [{}]".format(str(err)))
 PC.log_msg("device discover: Total time spent: {} seconds".format(int(time()) - start_time))
 return { 'found':len(db_new) }

#
# remove(id) and pop dns and ipam info
#
def remove(aDict):
 PC.log_msg("device_remove({})".format(aDict))
 with DB() as db:
  xist = db.do("SELECT hostname, mac, a_id, ptr_id, ipam_id FROM devices WHERE id = {}".format(aDict.get('id','0')))
  if xist == 0:
   ret = { 'res':'NOT_OK', 'a_id':0, 'ptr_id':0, 'ipam_id':0 }
  else:
   ret = db.get_row()
   ret['delete'] = db.do("DELETE FROM devices WHERE id = '{}'".format(aDict['id']))
   db.commit()
   ret['res'] = 'OK'
 return ret

#
# dump(columns)
# - columns is a string list
#
def dump_db(aDict):
 cols = aDict.get('columns','*')
 tbl  = aDict.get('table','devices')
 with DB() as db:
  res = db.do("SELECT {} FROM {}".format(cols,tbl))
 if res > 0:
  return db.get_rows()
 else:
  return []

#
# find_ip(ipam_sub_id, consecutive)
#
# - Find X consecutive ip from a particular subnet-id
# ipam_sub_id: X
# consecutive: X

def find_ip(aDict):
 PC.log_msg("device_find_ip({})".format(aDict))
 import sdcp.core.genlib as GL
 sub_id = aDict.get('ipam_sub_id')
 with DB() as db:
  db.do("SELECT subnet, INET_NTOA(subnet) as subasc, mask FROM subnets WHERE id = {}".format(sub_id))
  sub = db.get_row()
  db.do("SELECT ip FROM devices WHERE ipam_sub_id = {}".format(sub_id))
  iplist = db.get_rows_dict('ip')
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
 PC.log_msg("device_info({})".format(aDict))
 id = aDict['id']
 ret = {}
 with DB() as db:
  ret['exist'] = db.do("SELECT devices.*, subnets.subnet, a.name as a_name, INET_NTOA(ip) as ipasc FROM devices LEFT JOIN domains AS a ON devices.a_dom_id = a.id JOIN subnets ON devices.ipam_sub_id = subnets.id WHERE devices.id ='{}'".format(id))
  if ret['exist'] > 0:
   ret['info'] = db.get_row()
   ret['fqdn'] = ret['info']['hostname'] + "." + ret['info']['a_name']
   ret['res'] = 'OK'
   ret['booked'] = db.do("SELECT users.alias, bookings.user_id, NOW() < ADDTIME(time_start, '30 0:0:0.0') AS valid FROM bookings LEFT JOIN users ON bookings.user_id = users.id WHERE device_id ='{}'".format(id))
   if ret['booked'] > 0:
    ret['booking'] = db.get_row()
   ret['racked'] = db.do("SELECT rackinfo.*, INET_NTOA(consoles.ip) AS console_ip, consoles.name AS console_name FROM rackinfo LEFT JOIN consoles ON consoles.id = rackinfo.console_id WHERE rackinfo.device_id = {}".format(id))
   if ret['racked'] > 0:
    ret['rack'] = db.get_row()
  else:
   ret['res'] = 'NOT_OK'
 return ret

