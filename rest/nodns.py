"""NoDNS API module. Backend in case no DNS is available
Settings:
 - resolv.conf file

"""
__author__ = "Zacharias El Banna"                     
__version__ = "18.05.31GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

#################################### Domains #######################################
#
#
def domain_list(aDict):
 """NO OP

 Args:
  - filter (optional)
  - dict (optional)
  - exclude (optional)

 Output:
 """
 return {'xist':1,'domains':[{'id':0,'name':'local'}]}

#
#
def domain_info(aDict):
 """NO OP

 Args:
  - type (required)
  - master (required)
  - id (required)
  - name (required)
  - op (optional)

 Output:
 """
 ret = {'insert':0, 'update':0, 'xist':1, 'data':{'id':'0','name':'local','master':'127.0.0.1','type':'MASTER', 'notified_serial':0 }}
 return ret

#
#
def domain_delete(aDict):
 """NO OP

 Args:
  - id (required)

 Output:
 """
 return {'records':0,'domain':1}

#################################### Records #######################################
#
#
def record_list(aDict):
 """NO OP

 Args:
  - type (optional)
  - domain_id (optional)

 Output:
 """
 from sdcp.core.common import DB
 ret = {}
 with DB() as db:
  ret['count'] = db.do("SELECT devices.id, 0 AS domain_id, CONCAT(hostname,'.local') AS name, INET_NTOA(ia.ip) AS content, 'A' AS type, 3600 AS ttl FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id WHERE devices.a_dom_id = 0")
  ret['records']= db.get_rows()
 return ret

#
#
def record_info(aDict):
 """NO OP

 Args:
  - op (optional)
  - id (required)
  - domain_id (required)
  - name (optional)
  - content (optional)
  - type (optional)

 Output:
 """
 from sdcp.core.common import DB
 from sdcp.core.logger import log
 from json import dumps
 log("record_info",dumps(aDict))
 ret = {}
 with DB() as db:
  search = "ia.ip = INET_ATON('%s')"%aDict['content'] if aDict['id'] == 'new' and aDict.get('op') == 'update' and aDict.get('type') == 'A' else "devices.id = %s"%aDict['id']
  ret['xist'] = db.do("SELECT devices.id, 0 AS domain_id, CONCAT(hostname,'.local') AS name, INET_NTOA(ia.ip) AS content, 'A' AS type, 3600 AS ttl FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id WHERE devices.a_dom_id = 0 AND %s"%search)
  ret['data'] = db.get_row()
 return ret

#
#
def record_delete(aDict):
 """ NO OP

 Args:
  - id (required)

 Output:
 """
 return {'deleted':1}

############################### Tools #################################
#
#
def dedup(aDict):
 """ NO OP

 Args:

 Output:
 """
 return {'removed':[]}

#
#
def top(aDict):
 """ NO OP

 Args:
  - count (optional)

 Output:
 """
 return {'top':[],'who':[] }

