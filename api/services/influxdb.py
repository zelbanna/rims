"""InfluxDB API module. Implements influxdb interaction"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "TSDB"

############################### Databases #############################
#
#
def database_list(aCTX, aArgs):
 """Function list databases

 Args:
  - id (required). Server id on master node

 Output:
 """
 ret = {}
 db = aCTX.config['influxdb']
 try: ret['databases'] = [x[0] for x in aCTX.rest_call("%s/query"%(db['url']), aMethod='POST', aApplication = 'x-www-form-urlencoded', aArgs = {'q':'show databases'})['results'][0]['series'][0]['values']]
 except Exception as e:
  ret['status'] = 'NOT_OK'
  ret['info'] = str(e)
 else: ret['status'] = 'OK'
 return ret

################################# Points ##############################
#
#
def write_points(aCTX, aArgs):
 """ Function writes data points to configured influxdb

 Args:
  - id (required). Server id on master node
  - series (required)
  - value (required)
  - tags (optional)
  - precision (optional), (h,m,s,ms,u,ns), default to s

 Output:
  - status

 """
 ret = {}
 db = aCTX.config['influxdb']
 args = '%s,%s value=%s'%(aArgs['series'],"default" if not 'tags' in aArgs else ','.join(['%s=%s'%(x[0],x[1]) for x in aArgs['tags']]),aArgs['value'])
 try:  aCTX.rest_call("%s/write?db=%s&precision=%s"%(db['url'],db['database'],aArgs.get('precision','s')), aMethod = 'POST', aApplication = 'octet-stream', aArgs = args.encode())
 except Exception as e:
  ret['status'] = 'NOT_OK'
  ret['info'] = str(e)
 else: ret ['status'] = 'OK'
 return ret

################################# Tools ###############################
#
#
def stats(aCTX, aArgs):
 """Function shows live stats from node influxdb

 Args:
  - seconds (optional).

 Output:
 """
 ret = {}
 try:
  to = int(aArgs.get('seconds',10))
  ret['stats'] = aCTX.rest_call("%s/debug/requests?seconds=%i"%(aCTX.config['influxdb']['url'],to), aMethod = 'POST', aApplication = 'x-www-form-urlencoded', aTimeout = to + 5)
 except Exception as e:
  ret['status'] = 'NOT_OK'
  ret['info'] = str(e)
 else: ret['status'] = 'OK'
 return ret

#
#
def sync(aCTX, aArgs):
 """ Function creates database in case it does not exist

 Args:
  - id (required). Server id on master node

 Output:
 """
 ret = {}
 db = aCTX.config['influxdb']
 # INTERNAL rims.api.influxdb
 if not db['database'] in database_list(aCTX, aArgs)['databases']:
  try:
   for line in ["CREATE DATABASE %s"%db['database'], "CREATE RETENTION POLICY one_week ON %s DURATION 1w REPLICATION 1 default"%db['database']]:
    res = aCTX.rest_call("%s/query"%(db['url']), aApplication = 'x-www-form-urlencoded', aArgs = {'q':line}, aDataOnly = False, aMethod = 'POST')
  except Exception as e:
   ret['status'] = 'NOT_OK'
   ret['info'] = str(e)
  else:
   ret['status'] = 'OK' if res['code'] == 200 else 'NOT_OK'
 else:
  ret['status'] = 'OK'
  ret['extra'] = 'existed'
 return ret

#
#
def status(aCTX, aArgs):
 """Function shows stats form node influxdb...

 TODO++: Format nicer

 Args:
  - count (optional)

 Output:
 """
 ret = {}
 try:
  ret['stats'] = aCTX.rest_call("%s/query"%(aCTX.config['influxdb']['url']), aMethod = 'POST', aApplication = 'x-www-form-urlencoded', aArgs = {'q':'SHOW STATS'})['results'][0]
 except Exception as e:
  ret['status'] = 'NOT_OK'
  ret['info'] = str(e)
  ret['config'] = aCTX.config.get('influxdb')
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
 settings = aCTX.config.get('influxdb',{})
 params = ['url','database']
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}
