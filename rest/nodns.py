"""NoDNS API module. Backend in case no DNS is available
Settings:
 - resolv.conf file

"""
__author__ = "Zacharias El Banna"                     
__version__ = "18.04.07GA"
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
 return {'records':0,'domain':0}

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
 return {'count':0, 'records':[]}

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
 return {'xist':0, 'data':{'id':0,'domain_id':aDict.get('domain_id',0) ,'name':aDict.get('name','no_record'),'content':aDict.get('content','no_record'),'type':aDict.get('type','A'),'ttl':'3600' }}

#
#
def record_delete(aDict):
 """ NO OP

 Args:
  - id (required)

 Output:
 """
 return {'deleted':0}

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

