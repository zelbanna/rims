"""Module docstring.

PowerDNS API module

"""
__author__ = "Zacharias El Banna"                     
__version__ = "17.10.4"
__status__ = "Production"

import sdcp.PackageContainer as PC

#
# Call removes name duplicates.. (assume order by name => duplicate names :-))
#
def cleanup(aDict):
 from sdcp.core.dbase import DB
 with DB(PC.dnsdb['dbname'],'localhost',PC.dnsdb['username'],PC.dnsdb['password']) as db:
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
  db.commit()
 return {'removed':remove}

#
# dns top lookups
#
def top(aDict):
 import sdcp.core.genlib as GL
 count = int(aDict.get('count',10))
 fqdn_top = {}                
 fqdn_who = {}
 with open(PC.dnsdb['logfile'],'r') as log:
  for line in log:
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


#
# Return domains name + id
#
def domains(aDict):
 from sdcp.core.dbase import DB
 with DB(PC.dnsdb['dbname'],'localhost',PC.dnsdb['username'],PC.dnsdb['password']) as db:
  res = db.do("SELECT id, name FROM domains")
  rows = db.get_rows()
 return rows

#
# lookup ( name, a_dom_id, ip)
#
def lookup(aDict):
 import sdcp.core.genlib as GL
 PC.log_msg("DNS  lookup - input:{}".format(aDict.values()))  
 ptr  = GL.ip2arpa(aDict['ip'])
 from sdcp.core.dbase import DB
 with DB(PC.dnsdb['dbname'],'localhost',PC.dnsdb['username'],PC.dnsdb['password']) as db:
  res = db.do("SELECT id,name FROM domains WHERE id = {} OR name = '{}'".format(aDict['a_dom_id'],ptr))
  domains = db.get_rows()
  if res == 2:
   domain     = domains[0]['name'] if domains[1]['name'] == ptr else domains[1]['name']
   ptr_dom_id = domains[1]['id']   if domains[1]['name'] == ptr else domains[0]['id']
  else:
   domain     = domains[0]['name']
   ptr_dom_id = '0'
  fqdn    = aDict['name'] + "." + domain
  db.do("SELECT id,content FROM records WHERE type = 'A' and domain_id = {} and name = '{}'".format(aDict['a_dom_id'],fqdn))
  a_record = db.get_row()
  db.do("SELECT id,content FROM records WHERE type = 'PTR' and domain_id = {} and name = '{}'".format(ptr_dom_id,GL.ip2ptr(aDict['ip']))) 
  p_record = db.get_row()
 retvals = {}
 if a_record and (a_record.get('content',None) == aDict['ip']):
  retvals['a_id'] = a_record.get('id') 
 if p_record and p_record.get('content',None):
  retvals['ptr_id'] = p_record.get('id')
  retvals['ptr_dom_id'] = ptr_dom_id
 return retvals

#
# update( ip, name, a_dom_id , a_id, ptr_id )
#
def update(aDict):
 import sdcp.core.genlib as GL
 PC.log_msg("DNS  update - input:{}".format(aDict.values()))
 from time import strftime
 serial  = strftime("%Y%m%d%H")
 ptr     = GL.ip2ptr(aDict['ip'])
 retvals = {}
 from sdcp.core.dbase import DB
 with DB(PC.dnsdb['dbname'],'localhost',PC.dnsdb['username'],PC.dnsdb['password']) as db:
  res = db.do("SELECT id,name FROM domains WHERE id = {} OR name = '{}'".format(aDict['a_dom_id'],ptr.partition('.')[2]))
  domains = db.get_rows()
  if res == 2:
   domain     = domains[0]['name'] if domains[1]['name'] == ptr else domains[1]['name']
   ptr_dom_id = domains[1]['id']   if domains[1]['name'] == ptr else domains[0]['id']
  else:
   domain     = domains[0]['name']
   ptr_dom_id = None
  fqdn    = aDict['name'] + "." + domain

  if aDict['a_id'] != '0':
   retvals['a_op'] = "update"
   retvals['a_id'] = aDict['a_id']
   db.do("UPDATE records SET name = '{}', content = '{}', change_date='{}' WHERE id ='{}'".format(fqdn,aDict['ip'],serial,aDict['a_id']))
  else:
   db.do("INSERT INTO records (domain_id,name,type,content,ttl,change_date) VALUES('{}','{}','A','{}',3600,'{}')".format(aDict['a_dom_id'],fqdn,aDict['ip'],serial))
   retvals['a_op'] = "insert"
   retvals['a_id'] = db.get_last_id()

  if aDict['ptr_id'] != '0':
   retvals['ptr_id'] = aDict['ptr_id']
   retvals['ptr_op'] = "update"
   db.do("UPDATE records SET name = '{}', content = '{}', change_date='{}' WHERE id ='{}'".format(ptr,fqdn,serial,aDict['ptr_id']))
  elif aDict['ptr_id'] == '0' and ptr_dom_id:
   db.do("INSERT INTO records (domain_id,name,type,content,ttl,change_date) VALUES('{}','{}','PTR','{}',3600,'{}')".format(ptr_dom_id,ptr,fqdn,serial))
   retvals['ptr_op'] = "insert"
   retvals['ptr_id'] = db.get_last_id()

  db.commit()
 PC.log_msg("DNS  update - results: " + str(retvals))
 return retvals

#
#
#
def remove(aDict):
 PC.log_msg("DNS  remove - input:{}".format(aDict.values()))
 ares = 0
 pres = 0
 from sdcp.core.dbase import DB
 with DB(PC.dnsdb['dbname'],'localhost',PC.dnsdb['username'],PC.dnsdb['password']) as db:
  if aDict['a_id'] != '0':
   ares = db.do("DELETE FROM records WHERE id = '{}' and type = 'A'".format(aDict['a_id']))
  if aDict['ptr_id'] != '0':
   pres = db.do("DELETE FROM records WHERE id = '{}' and type = 'PTR'".format(aDict['ptr_id']))
  db.commit()
 PC.log_msg("DNS  remove - A:{} PTR:{}".format(str(ares),str(pres)))
 return { 'a':ares, 'ptr':pres }
