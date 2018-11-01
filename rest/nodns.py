"""NoDNS API module. Backend in case no DNS is available
Settings:
 - resolv.conf file

"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "DNS"

#################################### Domains #######################################
#
#
def domain_list(aDict, aCTX):
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
def domain_info(aDict, aCTX):
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
def domain_delete(aDict, aCTX):
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
def domain_save(aDict, aCTX):
 """NO OP

 Args:
  - id (required)

 Output:
 """
 return {'status':'NO_OP'}

#################################### Records #######################################
#
#
def record_list(aDict, aCTX):
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
def record_info(aDict, aCTX):
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
 if aDict['id'] == 'new':
  ret = {'found':False, 'data':{'id':0,'domain_id':0,'name':aDict.get('name','no_record'),'content':aDict.get('content','no_record'),'type':aDict.get('type','A'),'ttl':'3600' }}
 else:
  with aCTX.db as db:
   ret['found'] = (db.do("SELECT devices.id, 0 AS domain_id, CONCAT(hostname,'.local') AS name, INET_NTOA(ia.ip) AS content, 'A' AS type, 3600 AS ttl FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id WHERE devices.a_dom_id = 0 AND devices.id = %s"%aDict['id']) > 0)
   ret['data'] = db.get_row()
 return ret

#
#
def record_delete(aDict, aCTX):
 """ NO OP

 Args:
  - id (required)

 Output:
 """
 return {'deleted':1}

############################### Tools #################################
#
#
def sync(aDict, aCTX):
 """ NO OP

 Args:

 Output:
 """
 return {'removed':[]}

#
#
def status(aDict, aCTX):
 """ NO OP

 Args:
  - count (optional)

 Output:
 """
 return {'top':[],'who':[] }

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
 return {'status':'OK','code':0,'output':""}

