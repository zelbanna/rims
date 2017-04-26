"""Module docstring.

 Device restAPI module

"""
__author__ = "Zacharias El Banna"                     
__version__ = "10.5GA"
__status__ = "Production"

import sdcp.core.GenLib as GL

#
# Dump 2 JSON              
#
def dump_db(aDict):
 db = GL.DB()
 db.connect()
 res = db.do("SELECT * FROM devices")
 db.close()
 if res > 0:
  return db.get_all_rows()
 else:
  return []

#
# new(ip, ipam_sub_id, a_dom_id, hostname)
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
   mac = aDict.get('mac').replace(":","")
   if not (GL.sys_is_mac(mac)):
    mac = "000000000000"
   dbres = db.do("INSERT INTO devices (ip,mac,a_dom_id,ptr_dom_id,ipam_sub_id,hostname,snmp,model,type,fqdn,rack_size) VALUES({},x'{}',{},{},{},'{}','unknown','unknown','unknown','unknown',1)".format(ipint,mac,aDict.get('a_dom_id'),ptr_dom_id,aDict.get('ipam_sub_id'),aDict.get('hostname')))
   db.commit()
   ret = "Added ({})".format(dbres)
  else:
   xist = db.get_row()
   ret = "Existing ({}.{} - {})".format(xist['hostname'],xist['a_dom_id'],xist['id']) 
 db.close()
 return ret

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
#
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
