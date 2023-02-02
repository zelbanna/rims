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
def process(aRT, aArgs):
 try:
  res = aRT.influxdb.sync()
 except Exception as e:
  aRT.log(f"influxdb error: {str(e)}")
  ret = {'status':'NOT_OK','function':'influxdb_process','output':str(e)}
 else:
  if res >= 0:
   ret = {'status':'OK','function':'influxdb_process','output':res}
  else:
   ret = {'status':'NOT_OK','function':'influxdb_process','output':'inactive'}
 return ret

#
#
def query(aRT, aArgs):
 ret = {}
 try:
  res = aRT.influxdb.query(aArgs['query'])
  if any(res):
   ret['data'] = [{'field':r.get_field(), 'val':r.get_val()} for r in res.records]
   ret['status'] = 'OK'
  else:
   ret['status'] = 'NOT_OK'
   ret['info'] = 'empty'
 except Exception as e:
  return {'status':'NOT_OK','info':str(e)}
 else:
  return ret

################################# Service OPs #################################
#
#
def status(aRT, aArgs):
 """Function docstring for leases. No OP

 Args:
  - type (required)

 Output:
  - data
 """
 return {'data':aRT.influxdb.status(),'state':aRT.influxdb.active(), 'buffer':aRT.influxdb.buffer(), 'status':'OK' }

#
#
def sync(aRT, aArgs):
 """No OP

 Args:
  - id (required). Server id on master node

 Output:
  - code. (error code, optional)
  - output. (output from command)
  - status. (operation result)
 """
 ret = process(aRT, aArgs)
 ret.pop('function',None)
 return ret

#
#
def restart(aRT, aArgs):
 """Function provides restart capabilities of service

 Args:

 Output:
  - code
  - output
  - result 'OK'/'NOT_OK'
 """
 aRT.influxdb.active(True)
 return {'status':'OK','code':0,'output':"start"}

#
#
def parameters(aRT, aArgs):
 """ Function provides parameter mapping of anticipated config vs actual

 Args:

 Output:
  - status
  - parameters
 """
 settings = aRT.config.get('influxdb',{})
 params = ['url','org','token','bucket']
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}

#
#
def start(aRT, aArgs):
 """ Function provides start behavior

 Args:

 Output:
  - status
 """
 aRT.influxdb.active(True)
 return {'status':'OK'}

#
#
def stop(aRT, aArgs):
 """ Function provides stop behavior

 Args:

 Output:
  - status
 """
 aRT.influxdb.active(False)
 return {'status':'OK'}

#
#
def close(aRT, aArgs):
 """ Function provides closing behavior, wrapping up data and file handlers before closing

 Args:

 Output:
  - status
 """
 return process(aRT, aArgs)
