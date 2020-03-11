"""NoDNS API module. Backend in case no DNS is available, only on master node, records can be exported :-)

TODO: Add notified_serial to domain_cache and enable domain update
 
"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "DNS"

#################################### Domains #######################################
#
#
def domain_list(aCTX, aArgs = None):
 """ Function returns all domains by this DNS server

 Args:
  - filter (optional)
  - dict (optional)
  - exclude (optional)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  filter = "name %s LIKE '%%arpa' ORDER BY name"%('' if aArgs['filter'] == 'reverse' else "NOT") if 'filter' in aArgs else "TRUE"
  ret['count']   = db.do("SELECT foreign_id AS id, name,'MASTER' AS type,'127.0.0.1' AS master,0 AS notified_serial FROM domains JOIN servers ON domains.server_id = servers.id AND servers.node = '%s' JOIN service_types AS st ON servers.type_id = st.id AND st.service = 'nodns' WHERE %s"%(aCTX.node,filter))
  ret['data'] = db.get_rows() if not 'dict' in aArgs else db.get_dict(aArgs['dict'])
  if 'dict' in aArgs and 'exclude' in aArgs:
   ret['data'].pop(aArgs['exclude'],None)
 return ret

#
#
def domain_info(aCTX, aArgs = None):
 """ Function provide domain info and modification

 Args:
  - type (required)
  - master (required)
  - id (required)
  - name (required)
  - op (optional)

 Output:
 """
 ret = {'found':True, 'data':{'id':aArgs['id'],'name':aArgs.get('name','new_name'),'master':'127.0.0.1','type':'MASTER', 'notified_serial':0 }}
 op = aArgs.pop('op',None)
 with aCTX.db as db:
  if op == "update":
   if not aArgs['id'] == 'new':
    ret['update'] = True
   else:
    ret['insert'] = True
    db.do("SELECT max(id) + 1 AS next FROM domains")
    ret['data']['id'] = db.get_val('next')
  elif aArgs['id'] != 'new':
   db.do("SELECT name FROM domains WHERE foreign_id = %s"%aArgs['id'])
   ret['data']['name'] = db.get_val('name')
 return ret

#
#
def domain_delete(aCTX, aArgs = None):
 """ Let cache management handle this, NO OP

 Args:
  - id (required)

 Output:
  - records (number of removed records)
  - domain: True or false, did op succeed
 """
 return {'deleted':True,'records':0,'status':'OK'}

#################################### Records #######################################
#
#
def record_list(aCTX, aArgs = None):
 """ List device information where we have something -> i.e. on .local devices

 Args:
  - type (optional)
  - domain_id (optional)

 Output:
 """
 ret = {}
 select = []
 with aCTX.db as db:
  if 'domain_id' in aArgs:
   select.append("domain_id = %s"%aArgs['domain_id'])
  if 'type' in aArgs:
   select.append("type = '%s'"%aArgs['type'].upper())
  tune = " WHERE %s"%(" AND ".join(select)) if len(select) > 0 else ""
  ret['count'] = db.do("SELECT id, domain_id, name, type, content,ttl,DATE_FORMAT(change_date,'%%Y%%m%%d%%H%%i') AS change_date FROM domain_records %s ORDER BY type, name ASC"%tune)
  ret['data'] = db.get_rows()
 return ret

#
#
def record_info(aCTX, aArgs = None):
 """if new, do a mapping of either arpa or ip, else show ip info

 Args:
  - id (required)
  - domain_id (required)
  - op (optional) 'update'/'insert'
  - name (optional)
  - content (optional)
  - type (optional)

 Output:
 """
 id = aArgs.pop('id','new')
 op = aArgs.pop('op',None)
 aArgs.pop('change_date',None)
 ret = {'status':'OK'}
 with aCTX.db as db:
  if op:
   if str(id) in ['new','0'] and op == 'insert':
    aArgs.update({'ttl':aArgs.get('ttl','3600'),'type':aArgs['type'].upper(),'domain_id':str(aArgs['domain_id'])})
    ret['insert'] = 'OK'
    db.insert_dict('domain_records',aArgs,"ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)")
    id = db.get_last_id()
   elif op == 'update':
    ret['update'] = (db.update_dict('domain_records',aArgs,"id='%s'"%id) == 1)
  ret['status'] = 'OK' if (op is None) or ret.get('insert') or ret.get('update') else 'NOT_OK'
  ret['found'] = (db.do("SELECT id,domain_id,name,content,type,ttl FROM domain_records WHERE id = %s AND domain_id = %s"%(id,aArgs['domain_id'])) > 0)
  ret['data']  = db.get_row() if ret['found'] else {'id':'new','domain_id':aArgs['domain_id'],'name':'key','content':'value','type':'type-of-record','ttl':'3600' }
 return ret

#
#
def record_delete(aCTX, aArgs = None):
 """ Function deletes records info per type
 Args:
  - id (required)
  - domain_id (required)
  - type (optional)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  if (db.do("SELECT type FROM domain_records WHERE id = %(id)s AND domain_id = %(domain_id)s"%aArgs) > 0):
   ret['status'] = 'OK'
   type = db.get_val('type').lower()
   ret['deleted'] = (db.do("DELETE FROM domain_records WHERE id = %(id)s"%aArgs) > 0)
   if   type == 'a':
    ret['ipam'] = 'OK' if (db.do("UPDATE ipam_addresses SET a_id = 0 WHERE a_id = %s AND a_domain_id IN (SELECT id FROM domains WHERE foreign_id = %s)"%(aArgs['id'],aArgs['domain_id'])) > 0) else 'NOT_OK'
   elif type == 'ptr':
    ret['ipam'] = 'OK' if (db.do("UPDATE ipam_addresses SET ptr_id = 0 WHERE ptr_id = %s AND network_id IN (SELECT ine.id FROM ipam_networks AS ine LEFT JOIN domains ON ine.reverse_zone_id = domains.foreign_id WHERE domains.foreign_id = %s)"%(aArgs['id'],aArgs['domain_id'])) > 0) else 'NOT_OK'
   else:
    ret['ipam'] = 'NOT_OK'
  else:
   ret['status'] = 'NOT_OK'
   ret['info'] = 'record not found'
   ret['deleted'] = False
 return ret

############################### Tools #################################
#
#
def sync(aCTX, aArgs = None):
 """ Synchronize device table and recreate records

 Args:
  - id (required), server_id

 Output:
 """
 ret = {'update':0,'insert':0,'removed':0,'status':'OK'}
 with aCTX.db as db:
  # A records
  db.do("SELECT ia.id, INET_NTOA(ia.ip) AS ip, CONCAT(ia.hostname,'.',domains.name) AS fqdn, domains.foreign_id, ia.a_id, dr.id AS record_id, dr.name AS name, dr.content FROM ipam_addresses AS ia RIGHT JOIN domains ON ia.a_domain_id = domains.id LEFT JOIN domain_records AS dr ON ia.a_id = dr.id AND dr.type = 'A'WHERE domains.server_id = %s AND domains.type = 'forward' and ia.id IS NOT NULL AND (dr.id IS NULL OR (INET_NTOA(ia.ip) <> dr.content OR CONCAT(ia.hostname,'.',domains.name) <> dr.name OR ia.a_id <> dr.id))"%aArgs['id'])
  for rec in db.get_rows():
   if rec['record_id'] is None:
    ret['insert'] += db.do("INSERT INTO domain_records (domain_id,name,content,type) VALUES (%s,'%s','%s','A') ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)"%(rec['foreign_id'],rec['fqdn'],rec['ip']))
    record = db.get_last_id()
   else:
    ret['update'] += db.do("UPDATE domain_records SET domain_id = %s, name = '%s', content = '%s' WHERE id = %s AND type = 'A'"%(rec['foreign_id'],rec['fqdn'],rec['ip'],rec['record_id']))
    record = rec['record_id']
   db.do("UPDATE ipam_addresses SET a_id = %s WHERE id = %s"%(record,rec['id']))
  # PTR records
  db.do("SELECT ia.id, INET_NTOA(ia.ip) AS ip, CONCAT(ia.hostname,'.' ,a_domain.name) AS fqdn, ptr_domain.foreign_id, ia.ptr_id, dr.id AS record_id, dr.name AS name, dr.content, CONCAT(ip-network,'.',ptr_domain.name) AS ptr FROM ipam_addresses AS ia LEFT JOIN domains AS a_domain ON a_domain.id = ia.a_domain_id LEFT JOIN ipam_networks AS ine ON ia.network_id = ine.id RIGHT JOIN domains AS ptr_domain ON ptr_domain.id = ine.reverse_zone_id LEFT JOIN domain_records AS dr ON ia.ptr_id = dr.id AND dr.type = 'PTR' WHERE ptr_domain.server_id = %s AND ptr_domain.type = 'reverse' AND (ip-network) <= 256 AND ia.id IS NOT NULL AND (dr.id IS NULL OR (CONCAT(ip-network,'.',ptr_domain.name) <> dr.name OR CONCAT(ia.hostname,'.' ,a_domain.name) <> dr.content OR ia.ptr_id <> dr.id))"%aArgs['id'])
  for rec in db.get_rows():
   if rec['record_id'] is None:
    ret['insert'] += db.do("INSERT INTO domain_records (domain_id,name,content,type) VALUES (%s,'%s','%s','PTR') ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)"%(rec['foreign_id'],rec['ptr'],rec['fqdn']))
    record = db.get_last_id()
   else:
    ret['update'] += db.do("UPDATE domain_records SET domain_id = %s, name = '%s', content = '%s' WHERE id = %s AND type = 'PTR'"%(rec['foreign_id'],rec['ptr'],rec['fqdn'],rec['record_id']))
    record = rec['record_id']
   db.do("UPDATE ipam_addresses SET ptr_id = %s WHERE id = %s"%(record,rec['id']))

 return ret
#
#
def status(aCTX, aArgs = None):
 """ NO OP

 Args:
  - count (optional)

 Output:
 """
 return {'status':'OK','top':[],'who':[]}

#
#
def restart(aCTX, aArgs = None):
 """Function provides restart capabilities of service

 Args:

 Output:
  - code
  - output
  - status 'OK'/'NOT_OK'
 """
 return {'status':'OK','code':0,'output':""}

