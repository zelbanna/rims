"""Module docstring.

PowerDNS API module

"""
__author__ = "Zacharias El Banna"                     
__version__ = "17.11.01GA"
__status__ = "Production"

from .. import PackageContainer as PC
from ..core.dbase import DB
from ..core.logger import log

############################### Tools #################################
#
# Call removes name duplicates.. (assume order by name => duplicate names :-))
#
def dedup(aDict):
 log("powerdns_dedup({})".format(aDict))
 with DB(PC.dns['dbname'],'localhost',PC.dns['username'],PC.dns['password']) as db:
  db.do("SELECT id,name,content FROM records WHERE type = 'A' OR type = 'PTR' ORDER BY name")   
  rows = db.get_rows();
  remove = []
  previous = {'content':None,'name':None}
  for row in rows:
   if previous['content'] == row['content'] and previous['name'] == row['name']:
    db.do("DELETE from records WHERE id = '{}'".format(row['id'] if row['id'] > previous['id'] else previous['id']))
    row.pop('id')
    remove.append(row)
   else:
    previous = row
 return {'removed':remove}

#
# dns top lookups
#
def top(aDict):
 log("powerdns_top({})".format(aDict))
 from ..core import genlib as GL
 count = int(aDict.get('count',10))
 fqdn_top = {}
 fqdn_who = {}
 with open(PC.dns['logfile'],'r') as logfile:
  for line in logfile:
   parts = line.split()
   if not parts[5] == 'Remote':
    continue
   fqdn  = parts[8].split('|')[0][1:]
   fqdn_top[fqdn] = fqdn_top.get(fqdn,0)+1
   fqdn_who[fqdn+"#"+parts[6]] = fqdn_who.get(fqdn+"#"+parts[6],0)+1
 from collections import Counter
 top = map(lambda x: {'fqdn':x[0],'count':x[1]}, Counter(fqdn_top).most_common(count))
 who = []
 for item in  Counter(fqdn_who).most_common(count):
  parts = item[0].split('#')
  who.append({'fqdn':parts[0], 'who':parts[1], 'hostname': GL.get_host_name(parts[1]), 'count':item[1]})
 return {'top':top,'who':who }

#################################### Domains #######################################
#
#
def domains(aDict):
 log("powerdns_domains({})".format(aDict))
 ret = {}
 with DB(PC.dns['dbname'],'localhost',PC.dns['username'],PC.dns['password']) as db:
  ret['xist'] = db.do("SELECT domains.* FROM domains {} ORDER BY name".format('' if not aDict.get('id') else "WHERE id = {}".format(aDict['id'])))
  ret['domains'] = db.get_rows()
 return ret

#
# domain_lookup (id, domain_id)
#
def domain_lookup(aDict):
 log("powerdns_domain_lookup({})".format(aDict))
 ret = {}
 with DB(PC.dns['dbname'],'localhost',PC.dns['username'],PC.dns['password']) as db:
  ret['xist'] = db.do("SELECT domains.* FROM domains WHERE id = '{}'".format(aDict['id']))
  if ret['xist'] > 0:
   ret['data'] = db.get_row()
  else:
   ret['data'] = {'id':'new','name':'new-name','master':'ip-of-master','type':'MASTER' }
 return ret

#
def domain_update(aDict):
 log("powerdns_domain_update({})".format(aDict))
 ret = {'result':'OK'}
 with DB(PC.dns['dbname'],'localhost',PC.dns['username'],PC.dns['password']) as db:
  if aDict['id'] == 'new':
   # Create and insert a lot of records
   ret['xist'] = db.do("INSERT INTO domains(name, master, type) VALUES ('{}','{}','{}') ON DUPLICATE KEY UPDATE id = id".format(aDict['name'],aDict['master'],aDict['type']))
   ret['id']   = db.get_last_id() if ret['xist'] > 0 else "existing"
   if ret['id'] != 'existing':
    from time import strftime
    ret['serial'] = strftime("%Y%m%d%H")
    xist = db.do("SELECT domains.id AS domain_id, records.id AS record_id, records.name AS server, domains.name AS domain FROM records INNER JOIN domains ON domains.id = domain_id WHERE content = '{}' AND records.type ='A'".format(aDict['master']))
    ret['soa'] = db.get_row() if xist > 0 else {'server':'server.local','domain':'local'}
    db.do("INSERT INTO records(domain_id, name, content, type, ttl, change_date, prio) VALUES ({},'{}','{}','SOA',25200,'{}',0)".format(ret['id'],aDict['name'],"{} hostmaster.{} 0 21600 300 3600".format(ret['soa']['server'],ret['soa']['domain']),ret['serial'])) 
    db.do("INSERT INTO records(domain_id, name, content, type, ttl, change_date, prio) VALUES ({},'{}','{}','NS' ,25200,'{}',0)".format(ret['id'],aDict['name'],ret['soa']['server'],ret['serial'])) 
  else:
   ret['xist'] = db.do("UPDATE domains SET name = '{}', master = '{}', type = '{}' WHERE id = {}".format(aDict['name'],aDict['master'],aDict['type'],aDict['id']))
   ret['id']   = aDict['id']
 return ret

#
#
def domain_delete(aDict):
 log("powerdns_domain_delete({})".format(aDict))
 ret = {}
 with DB(PC.dns['dbname'],'localhost',PC.dns['username'],PC.dns['password']) as db:
  ret['deleted'] = db.do("DELETE FROM domains WHERE id = %i"%(int(aDict['id'])))
 return ret

#################################### Records #######################################
#
# records(type <'A'|'PTR'> | domain_id )
#
def records(aDict):
 log("powerdns_get_records({})".format(aDict))
 ret = {}
 try:    tune = ["domain_id = {}".format(aDict['domain_id'])]
 except: tune = []
 if aDict.get('type'):
  tune.append("type = '{}'".format(aDict['type'].upper()))
 with DB(PC.dns['dbname'],'localhost',PC.dns['username'],PC.dns['password']) as db:
  ret['count'] = db.do("SELECT id, domain_id AS dom_id, name, type, content,ttl,change_date FROM records WHERE {} ORDER BY type DESC, name".format(" AND ".join(tune)))
  ret['records'] = db.get_rows()
 return ret

#
# record_lookup (id, domain_id)
#
def record_lookup(aDict):
 log("powerdns_record_lookup({})".format(aDict))
 ret = {}
 with DB(PC.dns['dbname'],'localhost',PC.dns['username'],PC.dns['password']) as db:
  ret['xist'] = db.do("SELECT records.* FROM records WHERE id = '{}' AND domain_id = '{}'".format(aDict['id'],aDict['domain_id']))
  ret['data'] = db.get_row() if ret['xist'] > 0 else {'id':'new','domain_id':aDict['domain_id'],'name':'key','content':'value','type':'type-of-record','ttl':'3600' }
 return ret

#
# id/0/'new',dom_id,name,content,type (ttl)
def record_update(aDict):
 log("powerdns_record_update({})".format(aDict))
 from time import strftime
 aDict['change_date'] = strftime("%Y%m%d%H")
 aDict['ttl']  = aDict.get('ttl','3600')
 aDict['type'] = aDict['type'].upper()
 ret = {'id':aDict.pop('id',None)}
 with DB(PC.dns['dbname'],'localhost',PC.dns['username'],PC.dns['password']) as db:
  if ret['id'] == 'new' or str(ret['id']) == '0':
   ret['xist'] = db.do("INSERT INTO records(domain_id, name, content, type, ttl, change_date,prio) VALUES ({},'{}','{}','{}','{}','{}',0) ON DUPLICATE KEY UPDATE id = id".format(aDict['domain_id'],aDict['name'],aDict['content'],aDict['type'],aDict['ttl'],aDict['change_date']))
   ret['id']   = db.get_last_id() if ret['xist'] > 0 else "new"
  else:
   ret['xist'] = db.do("UPDATE records SET domain_id = {}, name = '{}', content = '{}', type = '{}', ttl = '{}', change_date = '{}',prio = 0 WHERE id = {}".format(aDict['domain_id'],aDict['name'],aDict['content'],aDict['type'],aDict['ttl'],aDict['change_date'],ret['id']))
 return ret

#
#
def record_delete(aDict):
 log("powerdns_record_delete({})".format(aDict))
 ret = {}
 with DB(PC.dns['dbname'],'localhost',PC.dns['username'],PC.dns['password']) as db:
  ret['deleted'] = db.do("DELETE FROM records WHERE id = '{}'".format(aDict['id']))
 return ret
