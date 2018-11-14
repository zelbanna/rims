"""Infoblox API module. Backend in case no DNS is available

"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

#################################### Domains #######################################
#
#
def domain_list(aCTX, aArgs = None):
 """NO OP

 Args:
  - filter (optional)
  - dict (optional)
  - exclude (optional)

 Output:
 """
 return {'count':1,'domains':[{'id':0,'name':'local'}]}

#
#
def domain_info(aCTX, aArgs = None):
 """NO OP

 Args:
  - type (required)
  - master (required)
  - id (required)
  - name (required)
  - op (optional)

 Output:
 """
 ret = {'insert':0, 'update':0, 'found':True, 'data':{'id':'0','name':'local','master':'127.0.0.1','type':'MASTER', 'notified_serial':0 }}
 return ret

#
#
def domain_delete(aCTX, aArgs = None):
 """NO OP

 Args:
  - id (required)

 Output:
  - records (number of removed records)
  - domain: True or false, did op succeed
 """
 return {'records':0,'domain':False}

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
 """NO OP

 Args:
  - type (optional)
  - domain_id (optional)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  ret['count'] = db.do("SELECT devices.id, 0 AS domain_id, CONCAT(hostname,'.local') AS name, INET_NTOA(ia.ip) AS content, 'A' AS type, 3600 AS ttl FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id WHERE devices.a_dom_id = 0")
  ret['records']= db.get_rows()
 return ret

#
#
def record_info(aCTX, aArgs = None):
 """NO OP if new, else show device id info

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
 if aArgs['id'] == 'new':
  ret = {'found':False, 'data':{'id':0,'domain_id':0,'name':aArgs.get('name','no_record'),'content':aArgs.get('content','no_record'),'type':aArgs.get('type','A'),'ttl':'3600' }}
 else:
  with aCTX.db as db:
   ret['found'] = (db.do("SELECT devices.id, 0 AS domain_id, CONCAT(hostname,'.local') AS name, INET_NTOA(ia.ip) AS content, 'A' AS type, 3600 AS ttl FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id WHERE devices.a_dom_id = 0 AND devices.id = %s"%aArgs['id']) > 0)
   ret['data'] = db.get_row()
 return ret

#
#
def record_delete(aCTX, aArgs = None):
 """ NO OP

 Args:
  - id (required)

 Output:
 """
 return {'deleted':1}

############################### Tools #################################
#
#
def dedup(aCTX, aArgs = None):
 """ NO OP

 Args:

 Output:
 """
 return {'removed':[]}

#
#
def top(aCTX, aArgs = None):
 """ NO OP

 Args:
  - count (optional)

 Output:
 """
 return {'top':[],'who':[] }

