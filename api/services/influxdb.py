"""InfluxDB service API module.

Expects config parameters:
- url
- token
- org
- bucket (default bucket)

"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "TSDB"

#
#
def process(aCTX, aArgs):
 try:
  res = aCTX.influxdb.sync()
 except Exception as e:
  aCTX.log(f"influxdb error: {str(e)}")
  ret = {'status':'NOT_OK','function':'influxdb_process','output':str(e)}
 else:
  if res >= 0:
   ret = {'status':'OK','function':'influxdb_process','output':res}
  else:
   ret = {'status':'NOT_OK','function':'influxdb_process','output':'inactive'}
 return ret

################################# Service OPs #################################
#
#
def status(aCTX, aArgs):
 """Function docstring for leases. No OP

 Args:
  - type (required)

 Output:
  - data
 """
 return {'data':aCTX.influxdb.status(),'state':aCTX.influxdb.active(), 'status':'OK' }

#
#
def sync(aCTX, aArgs):
 """No OP

 Args:
  - id (required). Server id on master node

 Output:
  - code. (error code, optional)
  - output. (output from command)
  - status. (operation result)
 """
 ret = process(aCTX, aArgs)
 ret.pop('function',None)
 return ret

#
#
def restart(aCTX, aArgs):
 """Function provides restart capabilities of service

 Args:

 Output:
  - code
  - output
  - result 'OK'/'NOT_OK'
 """
 aCTX.influxdb.active(True)
 return {'status':'OK','code':0,'output':"start"}

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
 params = ['url','org','token','bucket']
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}

#
#
def start(aCTX, aArgs):
 """ Function provides start behavior

 Args:

 Output:
  - status
 """
 aCTX.influxdb.active(True)
 return {'status':'OK'}

#
#
def stop(aCTX, aArgs):
 """ Function provides stop behavior

 Args:

 Output:
  - status
 """
 aCTX.influxdb.active(False)
 return {'status':'OK'}

