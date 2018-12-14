"""PowerDNS API module. Provides powerdns specific REST interface. Essentially to create a GUI management for PowerDNS.
Settings:
 - database
 - username
 - password
 - logfile
 - master (IP of master)
 - soa (e.g. 'xyz.domain hostmaster.domain 0 86400 3600 604800')

"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "DNS"

from rims.core.common import DB
from time import strftime

#################################### Domains #######################################
#
#
def domain_list(aCTX, aArgs = None):
 """Function docstring TBD

 Args:
  - filter (optional)
  - dict (optional)
  - exclude (optional)

 Output:
 """
 ret = {}
 with DB(aCTX.config['powerdns']['database'],'localhost',aCTX.config['powerdns']['username'],aCTX.config['powerdns']['password']) as db:
  if aArgs.get('filter'):
   ret['count'] = db.do("SELECT domains.* FROM domains WHERE name %s LIKE '%%arpa' ORDER BY name"%('' if aArgs.get('filter') == 'reverse' else "NOT"))
  else:
   ret['count'] = db.do("SELECT domains.* FROM domains")
  ret['domains'] = db.get_rows() if not 'dict' in aArgs else db.get_dict(aArgs['dict'])
  if 'dict' in aArgs and 'exclude' in aArgs:
   ret['domains'].pop(aArgs['exclude'],None)
 return ret

#
#
def domain_info(aCTX, aArgs = None):
 """Function docstring TBD

 Args:
  - type (required)
  - master (required)
  - id (required)
  - name (required)

 Output:
 """
 ret = {}
 id = aArgs.pop('id','new')
 op = aArgs.pop('op',None)
 with DB(aCTX.config['powerdns']['database'],'localhost',aCTX.config['powerdns']['username'],aCTX.config['powerdns']['password']) as db:
  if op == 'update':
   if id == 'new':
    # Create and insert a lot of records
    ret['insert'] = (db.insert_dict('domains',aArgs,'ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)') == 1)
    if ret['insert']:
     id = db.get_last_id()
     serial = strftime("%Y%m%d%H")
     # Find DNS for MASTER to be placed into SOA record
     master = db.do("SELECT records.name AS server, domains.name AS domain FROM records LEFT JOIN domains ON domains.id = records.domain_id WHERE content = '%s' AND records.type ='A'"%aArgs['master'])
     soa    = db.get_row() if master > 0 else {'server':'server.local','domain':'local'}
     sql = "INSERT INTO records(domain_id, name, content, type, ttl, change_date, prio) VALUES ('%s','%s','{}','{}' ,25200,'%s',0)"%(id,aArgs['name'],serial)
     db.do(sql.format("%s hostmaster.%s 0 21600 300 3600"%(soa['server'],soa['domain']),'SOA'))
     db.do(sql.format(soa['server'],'NS'))
     ret['extra'] = {'serial':serial,'master':master,'soa':soa}
    else:
     id = 'existing'
   else:
    ret['update'] = (db.update_dict('domains',aArgs,"id=%s"%id) == 1)

  ret['found'] = (db.do("SELECT id,name,master,type,notified_serial FROM domains WHERE id = '%s'"%id) > 0)
  ret['data'] = db.get_row() if ret['found'] else {'id':'new','name':'new-name','master':'ip-of-master','type':'MASTER', 'notified_serial':0 }
 return ret

#
#
def domain_delete(aCTX, aArgs = None):
 """Function docstring for domain_delete TBD

 Args:
  - id (required)

 Output:
  - records. number
  - domain. boolean
 """
 ret = {}
 with DB(aCTX.config['powerdns']['database'],'localhost',aCTX.config['powerdns']['username'],aCTX.config['powerdns']['password']) as db:
  id = int(aArgs['id'])
  ret['records'] = db.do("DELETE FROM records WHERE domain_id = %i"%id)
  ret['domain']  = (db.do("DELETE FROM domains WHERE id = %i"%(id)) == 1)
 return ret

#
#
def domain_save(aCTX, aArgs = None):
 """NO OP

 Args:
  - id (required)

 Output:
 """
 return {'status':'NO_OP'}

#################################### Records #######################################
#
#
def record_list(aCTX, aArgs = None):
 """Function docstring for records TBD

 Args:
  - type (optional)
  - domain_id (optional)

 Output:
 """
 ret = {}
 select = []
 if 'domain_id' in aArgs:
  select.append("domain_id = %s"%aArgs['domain_id'])
 if 'type' in aArgs:
  select.append("type = '%s'"%aArgs['type'].upper())
 tune = " WHERE %s"%(" AND ".join(select)) if len(select) > 0 else ""
 with DB(aCTX.config['powerdns']['database'],'localhost',aCTX.config['powerdns']['username'],aCTX.config['powerdns']['password']) as db:
  ret['count'] = db.do("SELECT id, domain_id, name, type, content,ttl,change_date FROM records %s ORDER BY type, name ASC"%tune)
  ret['records'] = db.get_rows()
 return ret

#
#
def record_info(aCTX, aArgs = None):
 """Function docstring for record_info TBD

 Args:
  - id (optional required)
  - domain_id (required)
  - op (optional) 'update'/'insert'
  - name (optional)
  - content (optional)
  - type (optional)

 Output:
 """
 ret = {}
 id = aArgs.pop('id','new')
 op = aArgs.pop('op',None)
 with DB(aCTX.config['powerdns']['database'],'localhost',aCTX.config['powerdns']['username'],aCTX.config['powerdns']['password']) as db:
  if op:
   if str(id) in ['new','0'] and op == 'insert':
    aArgs.update({'change_date':strftime("%Y%m%d%H"),'ttl':aArgs.get('ttl','3600'),'type':aArgs['type'].upper(),'prio':'0','domain_id':str(aArgs['domain_id'])})
    ret['insert'] = (db.insert_dict('records',aArgs,"ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)") == 1)
    id = db.get_last_id() if ret['insert'] > 0 else "new"
   elif op == 'update':
    ret['update'] = (db.update_dict('records',aArgs,"id='%s'"%id) == 1)

  ret['status'] = 'OK' if (op is None) or ret.get('insert') or ret.get('update') else 'NOT_OK'
  ret['found'] = (db.do("SELECT records.* FROM records WHERE id = '%s' AND domain_id = '%s'"%(id,aArgs['domain_id'])) > 0)
  ret['data']  = db.get_row() if ret['found'] else {'id':'new','domain_id':aArgs['domain_id'],'name':'key','content':'value','type':'type-of-record','ttl':'3600' }
 return ret

#
#
def record_delete(aCTX, aArgs = None):
 """Function docstring for record_delete TBD

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with DB(aCTX.config['powerdns']['database'],'localhost',aCTX.config['powerdns']['username'],aCTX.config['powerdns']['password']) as db:
  ret['status'] = 'OK' if (db.do("DELETE FROM records WHERE id = '%s'"%(aArgs['id'])) > 0) else 'NOT_OK'
 return ret

############################### Tools #################################
#
#
def sync(aCTX, aArgs = None):
 """Function docstring for sync. Removes name duplicates.. (assume order by name => duplicate names :-))

 Args:

 Output:
 """
 with DB(aCTX.config['powerdns']['database'],'localhost',aCTX.config['powerdns']['username'],aCTX.config['powerdns']['password']) as db:
  db.do("SELECT id,name,content FROM records WHERE type = 'A' OR type = 'PTR' ORDER BY name")   
  rows = db.get_rows();
  remove = []
  previous = {'content':None,'name':None}
  for row in rows:
   if previous['content'] == row['content'] and previous['name'] == row['name']:
    db.do("DELETE FROM records WHERE id = '{}'".format(row['id'] if row['id'] > previous['id'] else previous['id']))
    row.pop('id',None)
    remove.append(row)
   else:
    previous = row
 return {'removed':remove}

#
#
def status(aCTX, aArgs = None):
 """Function docstring for top TBD

 Args:
  - count (optional)

 Output:
 """
 def GL_get_host_name(aIP):
  from socket import gethostbyaddr
  try:    return gethostbyaddr(aIP)[0].partition('.')[0]
  except: return None

 count = int(aArgs.get('count',10))
 fqdn_top = {}
 fqdn_who = {}
 with open(aCTX.config['powerdns']['logfile'],'r') as logfile:
  for line in logfile:
   parts = line.split()
   if not parts[5] == 'Remote':
    continue
   fqdn  = parts[8].split('|')[0][1:]
   fqdn_top[fqdn] = fqdn_top.get(fqdn,0)+1
   fqdn_who[fqdn+"#"+parts[6]] = fqdn_who.get(fqdn+"#"+parts[6],0)+1
 from collections import Counter
 top = [{'fqdn':x[0],'count':x[1]} for x in Counter(fqdn_top).most_common(count)]
 who = []
 for item in  Counter(fqdn_who).most_common(count):
  parts = item[0].split('#')
  who.append({'fqdn':parts[0], 'who':parts[1], 'hostname': GL_get_host_name(parts[1]), 'count':item[1]})
 return {'top':top,'who':who }

#
#
def restart(aCTX, aArgs = None):
 """Function provides restart capabilities of service

 Args:

 Output:
  - code
  - output
  - result 'OK'/'NOT_OK'
 """
 from subprocess import check_output, CalledProcessError
 ret = {}
 try:
  ret['output'] = check_output(aCTX.config['powerdns'].get('reload','service pdns restart').split()).decode()
  ret['code'] = 0
 except CalledProcessError as c:
  ret['code'] = c.returncode
  ret['output'] = c.output
 ret['status'] = 'NOT_OK' if ret['output'] else 'OK'
 return ret
