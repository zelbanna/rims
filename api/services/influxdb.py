"""InfluxDB2 API module. Implements influxdb wrapper"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "TSDB"

################################# Tools ###############################
#
#
def sync(aCTX, aArgs):
 """ NO OP for the moment

 Args:
  - id (required). Server id on master node

 Output:
 """
 return {'status':'NO_OP'}

#
#
def status(aCTX, aArgs):
 """Function shows stats from node influxdb2...

 Args:
  - count (optional)

 Output:
 """
 ret = {}
 try:
  ret['stats'] = aCTX.influxdb_client.health().to_dict()
 except Exception as e:
  ret['status'] = 'NOT_OK'
  ret['info'] = str(e)
  ret['config'] = aCTX.config['services'].get('influxdb')
 else:
  ret['status'] = 'OK'
 return ret

#
#
def restart(aCTX, aArgs):
 return {'status':'OK','output':"",'code':0}

#
#
def parameters(aCTX, aArgs):
 """ Function provides parameter mapping of anticipated config vs actual

 Args:

 Output:
  - status
  - parameters
 """
 settings = aCTX.config['services'].get('influxdb',{})
 params = ['url','org','version','token'] if settings.get('version',2) else ['url','version','username','password']
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}

#
#
def start(aCTX, aArgs):
 """ Function provides start behavior

 Args:

 Output:
  - status
 """
 return {'status':'NO OP'}

#
#
def stop(aCTX, aArgs):
 """ Function provides stop behavior

 Args:

 Output:
  - status
 """
 return {'status':'NO OP'}

#
#
def sync(aCTX, aArgs):
 """ Function creates database in case it does not exist, for v1

 Args:
  - id (required). Server id on master node

 Output:
 """
 ret = {'status':'OK'}
 db = aCTX.config['services']['influxdb']
 if db['version'] == 1:
  try:
   ret['databases'] = [x[0] for x in aCTX.rest_call("%s/query"%(db['url']), aMethod='POST', aApplication = 'x-www-form-urlencoded', aArgs = {'q':'show databases'})['results'][0]['series'][0]['values']]
   if 'rims' not in ret['databases']:
    try:
     for line in ["CREATE DATABASE %s"%db['database'], "CREATE RETENTION POLICY one_week ON %s DURATION 1w REPLICATION 1 default"%db['database']]:
      res = aCTX.rest_call("%s/query"%(db['url']), aApplication = 'x-www-form-urlencoded', aArgs = {'q':line}, aDataOnly = False, aMethod = 'POST')
    except Exception as e:
     ret['status'] = 'NOT_OK'
     ret['info'] = str(e)
    else:
     ret['status'] = 'OK' if res['code'] == 200 else 'NOT_OK'
   else:
    ret['extra'] = 'existed'
  except Exception as e:
   ret['status'] = 'NOT_OK'
   ret['info'] = str(e)
 return ret
