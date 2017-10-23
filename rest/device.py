"""Module docstring.

 Device restAPI module

"""
__author__ = "Zacharias El Banna"                     
__version__ = "17.10.4"
__status__ = "Production"

from sdcp.core.dbase import DB

#
# lookup_info(id)
#
#
def lookup_info(aDict):
 from sdcp.devices.DevHandler import device_detect
 id  = aDict.get('id')
 ret = {}
 with DB() as db:
  res = db.do("SELECT INET_NTOA(ip) as ipasc, hostname, ipam_sub_id, a_dom_id, ptr_dom_id FROM devices WHERE id = {}".format(id))
  dev = db.get_row()
  name = dev.get('hostname')
  ip   = dev.get('ipasc')
  entry = device_detect(ip)
  if entry:
   if entry['hostname'] != 'unknown':
    name = entry['hostname']
   db.do("UPDATE devices SET hostname = '{}', snmp = '{}', fqdn = '{}', model = '{}', type = '{}' WHERE id = '{}'".format(name,entry['snmp'],entry['fqdn'],entry['model'],entry['type'],id))
   ret['base'] ='True'
 
  if not name == 'unknown':
   import sdcp.PackageContainer as PC
   from sdcp.core.rest import call as rest_call
   vals   = rest_call(PC.dns['url'],"sdcp.rest.{}_lookup".format(PC.dns['type']),{ 'ip':ip, 'name':name, 'a_dom_id':dev.get('a_dom_id') })
   a_id   = vals.get('a_id','0')
   ptr_id = vals.get('ptr_id','0')
   ret['dns'] = str(vals)
   vals   = rest_call(PC.ipam['url'],"sdcp.rest.{}_lookup".format(PC.ipam['type']),{'ip':ip, 'ipam_sub_id':dev.get('ipam_sub_id') })
   ipam_id = vals.get('ipam_id','0')
   iptr_id = vals.get('ptr_id','0')
   ret['ipam'] = str(vals)
   ret['out-of-sync'] = (iptr_id != '0' and iptr_id != ptr_id)
   db.do("UPDATE devices SET ipam_id = {}, a_id = '{}', ptr_id = '{}' WHERE id = '{}'".format(ipam_id, a_id,ptr_id,id))
  db.commit()
 return ret

#
# update_info(id,**key:value pairs)
#
def update_info(aDict):
 import sdcp.core.genlib as GL
 from sdcp.core.dbase import DB
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
 import sdcp.core.genlib as GL
 ipint = GL.ip2int(aDict.get('ip'))
 ptr_dom = GL.ip2arpa(aDict.get('ip'))
 ret = {'res':'not_added', 'info':None}
 with DB() as db:
  in_sub = db.do("SELECT subnet FROM subnets WHERE id = {0} AND {1} > subnet AND {1} < (subnet + POW(2,(32-mask))-1)".format(aDict.get('ipam_sub_id'),ipint))
  if in_sub == 0:
   ret['info'] = "IP not in subnet range"
  elif aDict.get('hostname') == 'unknown':
   ret['info'] = "Hostname unknown not allowed"
  else:
   xist = db.do("SELECT id, hostname, a_dom_id, ptr_dom_id FROM devices WHERE ipam_sub_id = {} AND (ip = {} OR hostname = '{}')".format(aDict.get('ipam_sub_id'),ipint,aDict.get('hostname')))
   if xist == 0:
    res = db.do("SELECT id FROM domains WHERE name = '{}'".format(ptr_dom))
    ptr_dom_id = db.get_row().get('id') if res > 0 else 'NULL'
    mac = 0 if not GL.is_mac(aDict.get('mac',False)) else GL.mac2int(aDict['mac'])
    dbres = db.do("INSERT INTO devices (ip,mac,a_dom_id,ptr_dom_id,ipam_sub_id,hostname,snmp,model,type,fqdn) VALUES({},{},{},{},{},'{}','unknown','unknown','unknown','unknown')".format(ipint,mac,aDict.get('a_dom_id'),ptr_dom_id,aDict.get('ipam_sub_id'),aDict.get('hostname')))
    devid = db.get_last_id()
    if aDict.get('target') == 'rack_id' and aDict.get('arg'):
     db.do("INSERT INTO rackinfo SET device_id = {}, rack_id = {} ON DUPLICATE KEY UPDATE rack_unit = 0, rack_size = 1".format(devid,aDict.get('arg')))
    db.commit()
    ret['res']  = "added"
    ret['info'] = "DB:{} ID:{}".format(dbres,devid)
   else:
    dev = db.get_row()
    ret['info']  = "existing"
    ret['extra'] = "hostname:{0} id:{2} domain:{1}".format(dev['hostname'],dev['a_dom_id'],dev['id'])
 return ret

#
# discover(start, end, clear, a_dom_id, ipam_sub_id)
#
def discover(aDict):
 from time import time
 from threading import Thread, BoundedSemaphore
 from sdcp.devices.DevHandler import device_detect
 import sdcp.PackageContainer as PC
 import sdcp.core.genlib as GL
 start_time = int(time())
 PC.log_msg("device_discover: " + str(aDict))
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
   ptr_doms = db.get_all_dict('name')
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
# remove(id)
#
def remove(aDict):
 with DB() as db:
  res = db.do("SELECT hostname, mac, a_id, ptr_id, ipam_id FROM devices WHERE id = {}".format(aDict.get('id','0')))
  ddi = db.get_row()
  res = db.do("DELETE FROM devices WHERE id = '{0}'".format(aDict['id']))
  ret = { 'device': res }
  db.commit()
 import sdcp.PackageContainer as PC
 from sdcp.core.rest import call as rest_call
 if (ddi['a_id'] != '0') or (ddi['ptr_id'] != '0'):
  dres = rest_call(PC.dns['url'],"sdcp.rest.{}_remove".format(PC.dns['type']), { 'a_id':ddi['a_id'], 'ptr_id':ddi['ptr_id'] })
  ret['a'] = dres.get('a')
  ret['ptr'] = dres.get('ptr')
 if not ddi['ipam_id'] == '0':
  ret['ipam'] = rest_call(PC.ipam['url'],"sdcp.rest.{}_remove".format(PC.ipam['type']),{ 'ipam_id':ddi['ipam_id'] })
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
# find(ipam_sub_id, consecutive)
#
def find(aDict):
 import sdcp.core.genlib as GL
 with DB() as db:
  db.do("SELECT subnet, mask FROM subnets WHERE id = {}".format(aDict.get('ipam_sub_id')))
  sub = db.get_row()
  db.do("SELECT ip FROM devices WHERE ipam_sub_id = {}".format(aDict.get('ipam_sub_id')))
  iplist = db.get_all_dict('ip')
 start = None
 ret = { 'subnet':GL.int2ip(sub.get('subnet')) }
 for ip in range(sub.get('subnet') + 1,sub.get('subnet') + 2**(32-sub.get('mask'))-1):
  if not iplist.get(ip,False):
   if start:
    count = count - 1
    if count == 1:
     ret['start'] = GL.int2ip(start)
     ret['end'] = GL.int2ip(start+int(aDict.get('consecutive'))-1)
     break
   else:
    count = int(aDict.get('consecutive'))
    start = ip
  else:
   start = None
 return ret
