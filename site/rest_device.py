"""Module docstring.

 Device restAPI module

"""
__author__ = "Zacharias El Banna"                     
__version__ = "10.5GA"
__status__ = "Production"

import sdcp.core.GenLib as GL

#
# lookup_info(id)
#
#
def lookup_info(aDict):
 from sdcp.devices.DevHandler import device_detect
 id  = aDict.get('id')
 db  = GL.DB()
 db.connect()
 res = db.do("SELECT INET_NTOA(ip) as ipasc, hostname, ipam_sub_id, a_dom_id, ptr_dom_id FROM devices WHERE id = {}".format(id))
 ret = {}
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
  from rest_ddi import dns_lookup, ipam_lookup
  vals   = dns_lookup({ 'ip':ip, 'name':name, 'a_dom_id':dev.get('a_dom_id') })
  a_id   = vals.get('a_id','0')
  ptr_id = vals.get('ptr_id','0')
  ret['dns'] = str(vals)
  vals   = ipam_lookup({'ip':ip, 'ipam_sub_id':dev.get('ipam_sub_id') })
  ipam_id = vals.get('ipam_id','0')
  iptr_id = vals.get('ptr_id','0')
  ret['ipam'] = str(vals)
  ret['out-of-sync'] = (iptr_id != '0' and iptr_id != ptr_id)
  db.do("UPDATE devices SET ipam_id = {}, a_id = '{}', ptr_id = '{}' WHERE id = '{}'".format(ipam_id, a_id,ptr_id,id))
 db.commit()
 db.close()
 return ret

#
# update_info(id,**key:value pairs)
#
def update_info(aDict):
 id   = aDict.pop('id',None)
 keys = aDict.keys()
 if keys:
  db = GL.DB()
  db.connect()
  for fkey in keys:
   # fkey = table _ key
   (table, void, key) = fkey.partition('_')
   data = aDict.get(fkey)
   if not (key[0:3] == 'pem' and key[5:] == 'pdu_slot_id'):
    if data == 'NULL':
     db.do("UPDATE devices SET {0}=NULL WHERE id = '{1}'".format(key,id))
    else:
     db.do("UPDATE devices SET {0}='{1}' WHERE id = '{2}'".format(key,data,id))
   else:
    pem = key[:4]
    [pemid,pemslot] = data.split('.')
    db.do("UPDATE devices SET {0}_pdu_id={1}, {0}_pdu_slot ='{2}' WHERE id = '{3}'".format(pem,pemid,pemslot,id))
  db.commit()
  db.close()
 return "update_values:" + ", ".join(keys)

#
# new(ip, hostname, ipam_sub_id, a_dom_id, mac)
#
def new(aDict):
 ipint = GL.sys_ip2int(aDict.get('ip'))
 ptr_dom = GL.sys_ip2arpa(aDict.get('ip'))
 db = GL.DB()
 db.connect()
 xist  = db.do("SELECT subnet FROM subnets WHERE id = {0} AND {1} > subnet AND {1} < (subnet + POW(2,(32-mask))-1)".format(aDict.get('ipam_sub_id'),ipint))
 if xist == 0:
  ret = "IP not in subnet range"
 elif not aDict.get('hostname') == 'unknown':
  xist = db.do("SELECT devices.id, hostname, a_dom_id, ptr_dom_id FROM devices WHERE ipam_sub_id = {} AND ip = {}".format(aDict.get('ipam_sub_id'),ipint))
  if xist == 0:
   res = db.do("SELECT id FROM domains WHERE name = '{}'".format(ptr_dom))
   ptr_dom_id = db.get_row().get('id') if res > 0 else 'NULL'
   mac = aDict.get('mac','000000000000').replace(":","")
   if not (GL.sys_is_mac(mac)):
    mac = "000000000000"
   dbres = db.do("INSERT INTO devices (ip,mac,a_dom_id,ptr_dom_id,ipam_sub_id,hostname,snmp,model,type,fqdn,rack_size) VALUES({},x'{}',{},{},{},'{}','unknown','unknown','unknown','unknown',1)".format(ipint,mac,aDict.get('a_dom_id'),ptr_dom_id,aDict.get('ipam_sub_id'),aDict.get('hostname')))
   db.commit()
   ret = "Added ({})".format(dbres)
  else:
   xist = db.get_row()
   ret = "Existing host:{0}({2}) domain:{}".format(xist['hostname'],xist['a_dom_id'],xist['id']) 
 db.close()
 return ret

#
# discover(start, end, clear, a_dom_id, ipam_sub_id)
#
def discover(aDict):
 from time import time
 from threading import Thread, BoundedSemaphore
 from sdcp.devices.DevHandler import device_detect
 start_time = int(time())
 GL.sys_log_msg("rest_device_discover: " + str(aDict))
 ip_start = aDict.get('start')
 ip_end   = aDict.get('end')
 db = GL.DB()
 db.connect()
 db_old, db_new = {}, {}
 if aDict.get('clear',False):
  db.do("TRUNCATE TABLE devices")
  db.commit()
 else:
  res  = db.do("SELECT ip FROM devices WHERE ip >= {} and ip <= {}".format(ip_start,ip_end))
  rows = db.get_all_rows()
  for item in rows:
   db_old[item.get('ip')] = True
 try:
  sema = BoundedSemaphore(10)
  for ip in GL.sys_ipint2range(ip_start,ip_end):
   if db_old.get(GL.sys_ip2int(ip),None):
    continue
   sema.acquire()
   t = Thread(target = device_detect, args=[ip, db_new, sema])
   t.name = "Detect " + ip
   t.start()
  
  # Join all threads by acquiring all semaphore resources
  for i in range(10):
   sema.acquire()
  # We can do insert as either we clear or we skip existing :-)
  sql = "INSERT INTO devices (ip, a_dom_id, ptr_dom_id, ipam_sub_id, hostname, snmp, model, type, fqdn, rack_size) VALUES ({0},{1},{2},{3},'{4}','{5}','{6}','{7}','{8}',{9})"
  res = db.do("SELECT id,name FROM domains WHERE name LIKE '%arpa%'")
  ptr_doms = db.get_all_dict('name')
  for ip,entry in db_new.iteritems():
   ptr_dom_id = ptr_doms.get(GL.sys_ip2arpa(ip),{ 'id':'NULL' })['id']
   db.do(sql.format(GL.sys_ip2int(ip), aDict.get('a_dom_id'), ptr_dom_id, aDict.get('ipam_sub_id'), entry['hostname'],entry['snmp'],entry['model'],entry['type'],entry['fqdn'],entry['rack_size']))
  else:
   db.commit()
 except Exception as err:
  GL.sys_log_msg("device discover: Error [{}]".format(str(err)))
 db.close()
 GL.sys_log_msg("device discover: Total time spent: {} seconds".format(int(time()) - start_time))
 return { 'found':len(db_new) }

#
# remove(id)
#
def remove(aDict):
 db = GL.DB()
 db.connect()
 res = db.do("SELECT a_id, ptr_id, ipam_id FROM devices WHERE id = {}".format(aDict.get('id','0')))
 ddi = db.get_row()
 res = db.do("DELETE FROM devices WHERE id = '{0}'".format(aDict['id']))
 ret = { 'device': dev }
 db.commit()
 db.close()
 if (ddi['a_id'] != '0') or (ddi['ptr_id'] != '0'):
  from rest_ddi import dns_remove
  dres = dns_remove( { 'a_id':ddi['a_id'], 'ptr_id':ddi['ptr_id'] })
  ret['a'] = dres.get('a')
  ret['ptr'] = dres.get('ptr')
 if not ddi['ipam_id'] == '0':
  from rest_ddi import ipam_remove
  ret['ipam'] = ipam_remove({ 'ipam_id':ddi['ipam_id'] })
 return ret

#
# dump(columns)
# - columns is a string list
#
def dump_db(aDict):
 db = GL.DB()
 db.connect()
 cols = aDict.get('columns','*')
 res = db.do("SELECT {} FROM devices".format(cols))
 db.close()
 if res > 0:
  return db.get_all_rows()
 else:
  return []

#
# find(ipam_sub_id, consecutive)
#
def find(aDict):
 db = GL.DB()
 db.connect()
 db.do("SELECT subnet, mask FROM subnets WHERE id = {}".format(aDict.get('ipam_sub_id')))
 sub = db.get_row()
 db.do("SELECT ip FROM devices WHERE ipam_sub_id = {}".format(aDict.get('ipam_sub_id')))
 iplist = db.get_all_dict('ip')
 db.close()
 start = None
 ret = { 'subnet':GL.sys_int2ip(sub.get('subnet')) }
 for ip in range(sub.get('subnet') + 1,sub.get('subnet') + 2**(32-sub.get('mask'))-1):
  if not iplist.get(ip,False):
   if start:
    count = count - 1
    if count == 1:
     ret['start'] = GL.sys_int2ip(start)
     ret['end'] = GL.sys_int2ip(start+int(aDict.get('consecutive'))-1)
     break
   else:
    count = int(aDict.get('consecutive'))
    start = ip
  else:
   start = None
 return ret
