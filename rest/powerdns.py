"""Module docstring.

PowerDNS API module

"""
__author__ = "Zacharias El Banna"                     
__version__ = "17.11.01GA"
__status__ = "Production"

from sdcp import PackageContainer as PC
from sdcp.core.dbase import DB
from sdcp.core.logger import log

#
# Call removes name duplicates.. (assume order by name => duplicate names :-))
#
def cleanup(aDict):
 log("powerdns_cleanup({})".format(aDict))
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
 return {'res':'OK', 'removed':remove}

#
# dns top lookups
#
def top(aDict):
 log("powerdns_top({})".format(aDict))
 from sdcp.core import genlib as GL
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
 return {'res':'OK', 'top':top,'who':who }

#
#
def domains(aDict):
 log("powerdns_domains({})".format(aDict))
 ret = {'res':'OK'}
 with DB(PC.dns['dbname'],'localhost',PC.dns['username'],PC.dns['password']) as db:
  ret['xist'] = db.do("SELECT domains.* FROM domains {} ORDER BY name".format('' if not aDict.get('id') else "WHERE id = {}".format(aDict['id'])))
  ret['domains'] = db.get_rows()
 return ret

#
# lookup_a ( name, a_dom_id)
#
def lookup_a(aDict):
 log("powerdns_lookup_a({})".format(aDict))
 ret = {}
 with DB(PC.dns['dbname'],'localhost',PC.dns['username'],PC.dns['password']) as db:
  res = db.do("SELECT name FROM domains WHERE id = '{}'".format(aDict['a_dom_id']))
  ret['domain'] = db.get_val('name') if res > 0 else 'unknown'
  ret['xist'] = db.do("SELECT id, content AS ip FROM records WHERE type = 'A' AND domain_id = {} AND name = '{}'".format(aDict['a_dom_id'],"{}.{}".format(aDict['name'],ret['domain'])))
  if ret['xist'] > 0:
   ret.update(db.get_row())
   ret['res']  = 'OK'
  else:
   ret['res']  = 'NOT_OK'
 return ret

#
# lookup_ptr (ip)
#
def lookup_ptr(aDict):
 log("powerdns_lookup_ptr({})".format(aDict))
 ret = {}
 with DB(PC.dns['dbname'],'localhost',PC.dns['username'],PC.dns['password']) as db:
  from sdcp.core import genlib as GL
  res = db.do("SELECT id FROM domains WHERE type = 'PTR' AND name = '{}'".format( GL.ip2arpa(aDict['ip']) ))
  ret['domain_id'] = db.get_val('id')
  ret['xist'] = db.do("SELECT id, content AS fqdn FROM records WHERE type = 'PTR' AND domain_id = {} AND name = '{}'".format(ret['domain_id'],GL.ip2ptr(aDict['ip'])))
  if ret['xist'] > 0:
   ret.update(db.get_row())
   ret['res'] = 'OK'
  else:
   ret['res'] = 'NOT_OK'
 return ret

#
# lookup_id (id)
#
def lookup_id(aDict):
 log("powerdns_lookup_id({})".format(aDict))
 ret = {}
 with DB(PC.dns['dbname'],'localhost',PC.dns['username'],PC.dns['password']) as db:
  ret['xist'] = db.do("SELECT domains.* FROM domains WHERE id = '{}'".format(aDict['id']))
  if ret['xist'] > 0:
   ret.update(db.get_row())
   ret['res'] = 'OK'
  else:
   ret['res'] = 'NOT_OK'
 return ret

#
# update( id, ip, fqdn, domain_id, type)
#
# A:  content = ip, name = fqdn
# PTR content = fqdn, name = ip2ptr(ip)
#
def update(aDict):
 log("powerdns_update({})".format(aDict))
 from time import strftime
 serial  = strftime("%Y%m%d%H")
 type = aDict['type'].upper()
 if type == 'A':
  cont = aDict['ip']
  name = aDict['fqdn']
 else:
  from sdcp.core import genlib as GL
  cont = aDict['fqdn']
  name = GL.ip2ptr(aDict['ip'])
 ret = {'res':'OK', 'type':type }
 with DB(PC.dns['dbname'],'localhost',PC.dns['username'],PC.dns['password']) as db:
  if str(aDict.get('id','0')) != '0':
   ret['update'] = db.do("UPDATE records SET name = '{}', content = '{}', change_date='{}' WHERE type = '{}' AND id ='{}'".format(name,cont,serial,type,aDict['id']))
   if ret['update'] == 0:
    ret['xist']= db.do("SELECT id FROM records WHERE name = '{}' AND content = '{}' AND type = '{}'".format(name,cont,type))
    if ret['xist'] == 1:
     ret['id']  = db.get_val('id')
     ret['res'] = "OK" if (ret['id'] == int(aDict['id'])) else "NOT_OK"
    else:
     ret['id']  = 0
     ret['res'] = 'NOT_OK'
   else:
    ret['id'] = aDict['id']
  else:
   ret['insert']= db.do("INSERT INTO records (name,content,type,domain_id,ttl,change_date) VALUES('{}','{}','{}','{}',3600,'{}')".format(name,cont,type,aDict['domain_id'],serial))
   ret['id']    = db.get_last_id()
 return ret

#
# records(type <'A'|'PTR'> | domain_id )
#
def records(aDict):
 log("powerdns_get_records({})".format(aDict))
 ret = {'res':'OK'}
 try:    tune = ["domain_id = {}".format(aDict['domain_id'])]
 except: tune = []
 if aDict.get('type'):
  tune.append("type = '{}'".format(aDict['type'].upper()))
 with DB(PC.dns['dbname'],'localhost',PC.dns['username'],PC.dns['password']) as db:
  ret['count'] = db.do("SELECT id, domain_id AS dom_id, name, type, content,ttl,change_date FROM records WHERE {} ORDER BY type DESC, name".format(" AND ".join(tune)))
  ret['records'] = db.get_rows()
 return ret

#
#
def record_remove(aDict):
 log("powerdns_remove({})".format(aDict))
 ret = {}
 with DB(PC.dns['dbname'],'localhost',PC.dns['username'],PC.dns['password']) as db:
  ret['xist'] = db.do("DELETE FROM records WHERE id = '{}'".format(aDict['id']))
  ret['res'] = 'OK' if ret['xist'] > 0 else 'NOT_OK'
 return ret
