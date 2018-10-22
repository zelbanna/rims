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
def domain_list(aDict, aCTX):
 """Function docstring TBD

 Args:
  - filter (optional)
  - dict (optional)
  - exclude (optional)

 Output:
 """
 ret = {}
 with DB(aCTX.settings['powerdns']['database'],'localhost',aCTX.settings['powerdns']['username'],aCTX.settings['powerdns']['password']) as db:
  if aDict.get('filter'):
   ret['count'] = db.do("SELECT domains.* FROM domains WHERE name %s LIKE '%%arpa' ORDER BY name"%('' if aDict.get('filter') == 'reverse' else "NOT"))
  else:
   ret['count'] = db.do("SELECT domains.* FROM domains")
  ret['domains'] = db.get_rows() if not aDict.get('dict') else db.get_dict(aDict.get('dict'))
  if aDict.get('dict') and aDict.get('exclude'):
   ret['domains'].pop(aDict.get('exclude'),None)
 return ret

#
#
def domain_info(aDict, aCTX):
 """Function docstring TBD

 Args:
  - type (required)
  - master (required)
  - id (required)
  - name (required)

 Output:
 """
 ret = {}
 id = aDict.pop('id','new')
 op = aDict.pop('op',None)
 with DB(aCTX.settings['powerdns']['database'],'localhost',aCTX.settings['powerdns']['username'],aCTX.settings['powerdns']['password']) as db:
  if op == 'update':
   if id == 'new':
    # Create and insert a lot of records
    ret['insert'] = db.insert_dict('domains',aDict,'ON DUPLICATE KEY UPDATE id = id')
    if ret['insert'] > 0:
     id = db.get_last_id()
     serial = strftime("%Y%m%d%H")
     # Find DNS for MASTER to be placed into SOA record
     master = db.do("SELECT records.name AS server, domains.name AS domain FROM records LEFT JOIN domains ON domains.id = records.domain_id WHERE content = '%s' AND records.type ='A'"%aDict['master'])
     soa    = db.get_row() if master > 0 else {'server':'server.local','domain':'local'}
     sql = "INSERT INTO records(domain_id, name, content, type, ttl, change_date, prio) VALUES ('%s','%s','{}','{}' ,25200,'%s',0)"%(id,aDict['name'],serial)
     db.do(sql.format("%s hostmaster.%s 0 21600 300 3600"%(soa['server'],soa['domain']),'SOA'))
     db.do(sql.format(soa['server'],'NS'))
     ret['extra'] = {'serial':serial,'master':master,'soa':soa}
    else:
     id = 'existing'
   else:
    ret['update'] = db.update_dict('domains',aDict,"id=%s"%id)

  ret['found'] = (db.do("SELECT id,name,master,type,notified_serial FROM domains WHERE id = '%s'"%id) > 0)
  ret['data'] = db.get_row() if ret['found'] else {'id':'new','name':'new-name','master':'ip-of-master','type':'MASTER', 'notified_serial':0 }
 return ret

#
#
def domain_delete(aDict, aCTX):
 """Function docstring for domain_delete TBD

 Args:
  - id (required)

 Output:
  - records. number
  - domain. boolean
 """
 ret = {}
 with DB(aCTX.settings['powerdns']['database'],'localhost',aCTX.settings['powerdns']['username'],aCTX.settings['powerdns']['password']) as db:
  id = int(aDict['id'])
  ret['records'] = db.do("DELETE FROM records WHERE domain_id = %i"%id)
  ret['domain']  = (db.do("DELETE FROM domains WHERE id = %i"%(id)) == 1)
 return ret

#
#
def domain_save(aDict, aCTX):
 """NO OP

 Args:
  - id (required)

 Output:
 """
 return {'result':'NO_OP'}

#################################### Records #######################################
#
#
def record_list(aDict, aCTX):
 """Function docstring for records TBD

 Args:
  - type (optional)
  - domain_id (optional)

 Output:
 """
 ret = {}
 select = []
 if aDict.get('domain_id'):
  select.append("domain_id = %s"%aDict.get('domain_id'))
 if aDict.get('type'):
  select.append("type = '%s'"%aDict.get('type').upper())
 tune = " WHERE %s"%(" AND ".join(select)) if len(select) > 0 else ""
 with DB(aCTX.settings['powerdns']['database'],'localhost',aCTX.settings['powerdns']['username'],aCTX.settings['powerdns']['password']) as db:
  ret['count'] = db.do("SELECT id, domain_id, name, type, content,ttl,change_date FROM records %s ORDER BY type, name ASC"%tune)
  ret['records'] = db.get_rows()
 return ret

#
#
def record_info(aDict, aCTX):
 """Function docstring for record_info TBD

 Args:
  - op (optional)
  - id (required)
  - domain_id (required)
  - name (optional)
  - content (optional)
  - type (optional)

 Output:
 """
 ret = {}
 id = aDict.pop('id','new')
 op = aDict.pop('op',None)
 with DB(aCTX.settings['powerdns']['database'],'localhost',aCTX.settings['powerdns']['username'],aCTX.settings['powerdns']['password']) as db:
  if op == 'update':
   if str(id) in ['new','0']:
    aDict.update({'change_date':strftime("%Y%m%d%H"),'ttl':aDict.get('ttl','3600'),'type':aDict['type'].upper(),'prio':'0','domain_id':str(aDict['domain_id'])})
    ret['insert'] = db.insert_dict('records',aDict,"ON DUPLICATE KEY UPDATE id = id")
    id = db.get_last_id() if ret['insert'] > 0 else "new"
   else:
    ret['update'] = db.update_dict('records',aDict,"id='%s'"%id)
 
  ret['found'] = (db.do("SELECT records.* FROM records WHERE id = '%s' AND domain_id = '%s'"%(id,aDict['domain_id'])) > 0)
  ret['data']  = db.get_row() if ret['found'] else {'id':'new','domain_id':aDict['domain_id'],'name':'key','content':'value','type':'type-of-record','ttl':'3600' }
 return ret

#
#
def record_delete(aDict, aCTX):
 """Function docstring for record_delete TBD

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with DB(aCTX.settings['powerdns']['database'],'localhost',aCTX.settings['powerdns']['username'],aCTX.settings['powerdns']['password']) as db:
  ret['deleted'] = (db.do("DELETE FROM records WHERE id = '%s'"%(aDict['id'])) > 0)
 return ret

############################### Tools #################################
#
#
def sync(aDict, aCTX):
 """Function docstring for sync. Removes name duplicates.. (assume order by name => duplicate names :-))

 Args:

 Output:
 """
 with DB(aCTX.settings['powerdns']['database'],'localhost',aCTX.settings['powerdns']['username'],aCTX.settings['powerdns']['password']) as db:
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
def status(aDict, aCTX):
 """Function docstring for top TBD

 Args:
  - count (optional)

 Output:
 """
 def GL_get_host_name(aIP):
  from socket import gethostbyaddr
  try:    return gethostbyaddr(aIP)[0].partition('.')[0]
  except: return None

 count = int(aDict.get('count',10))
 fqdn_top = {}
 fqdn_who = {}
 with open(aCTX.settings['powerdns']['logfile'],'r') as logfile:
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
def restart(aDict, aCTX):
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
  ret['output'] = check_output(aCTX.settings['powerdns'].get('reload','service pdns restart').split()).decode()
 except CalledProcessError as c:
  ret['code'] = c.returncode
  ret['output'] = c.output
 ret['result'] = 'NOT_OK' if ret['output'] else 'OK'
 return ret
