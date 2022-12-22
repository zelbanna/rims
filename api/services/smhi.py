"""SMHI API module. Implements logics to reuse scheduler and influxdb handler for SMHI weather analysis data. Always run ever hour  """
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "TELEMETRY"

from datetime import datetime

#
#
def process(aRT, aArgs):
 """Function checks SMHI API, process data and queue reporting to influxDB bucket

 Args:

 Output:
  - status
 """
 ret = {'status':'OK','function':'smhi_process'}
 state = aRT.cache.get('smhi',{'status':'forced','timestamp':0})
 if state['status'] != 'inactivate':
  config = aRT.config['services']['smhi']
  res = sync(aRT,None)
  if res['status'] == 'OK':
   records = []
   for stage in ['weather','forecast']:
    data = res[stage]['data']
    tmpl = '{0},origin=smhi,type={1},system_id=smhi,label=%s %s {2}'.format(config.get('measurement','smhi'),stage,res[stage]['ts'])
    for tp in ['weather','wind','extra','rain']:
     records.append(tmpl%(tp,",".join("%s=%s"%(k,v) for k,v in data[tp].items())))

   if state['status'] == 'active':
    aRT.influxdb.write(records, config['bucket'])
   if aRT.debug:
    ret['data'] = records
  else:
   ret['status'] = 'NOT_OK'
   ret['info'] = 'no_updated_data'
 else:
  ret['status'] = 'NOT_OK'
  ret['info'] = 'inactive'
 return ret

########################################################################################
#
#
def status(aRT, aArgs):
 """Function retrives the current 24h historical data from SMHI

  https://opendata-download-metanalys.smhi.se/api/category/mesan1g/version/2/geotype/point/lon/16/lat/58/data.json

 Args:
  - type (required)

 Output:
  - weather
  - forecast
 """
 ret = {}
 config = aRT.config['services']['smhi']
 url_forecast = 'https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{longitude}/lat/{latitude}/data.json'.format(**config)
 url_weather = 'https://opendata-download-metanalys.smhi.se/api/category/mesan1g/version/2/geotype/point/lon/{longitude}/lat/{latitude}/data.json'.format(**config)
 return {'status':'OK','forecast':url_forecast,'weather':url_weather}


#
#
def sync(aRT, aArgs):
 """ No-Op

 Args:
  - id (required). Server id on master node

 Output:
  - weather. Object
  - forecast. Object
  - status. (operation result)
 """
 ret = {}
 config = aRT.config['services']['smhi']
 url_forecast = 'https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{longitude}/lat/{latitude}/data.json'.format(**config)
 url_weather = 'https://opendata-download-metanalys.smhi.se/api/category/mesan1g/version/2/geotype/point/lon/{longitude}/lat/{latitude}/data.json'.format(**config)
 try:
  weather = aRT.rest_call(url_weather, aSSL = aRT.ssl, aMethod = 'GET')['timeSeries'][0]
  forecast = aRT.rest_call(url_forecast, aSSL = aRT.ssl, aMethod = 'GET')['timeSeries'][config.get('forecasting',12)]
 except Exception as e:
  ret['info'] = str(e)
  ret['status'] = 'NOT_OK'
 else:
  xlate = {
   't':('temperature','weather'),
   'tiw':('wet_bulb','weather'),
   'r':('humidity','weather'),
   'msl':('pressure','weather'),
   'gust':('gust','wind'),
   'wd':('deg','wind'),
   'ws':('speed','wind'),
   'prec1':('1h','rain'),
   'pmean':('1h','rain'),
   'prec3':('3h','rain'),
   'vis':('visibility','extra'),
   'c_sigfr':('cloud_significant','extra'),
   'tcc':('cloud_cover','extra'),
   'tcc_mean':('cloud_cover','extra'),
   'tstm':('thunder','extra')
  }
  ret['state'] = aRT.cache.get('smhi')
  for stage in [('weather',weather), ('forecast',forecast)]:
   measure = stage[1]
   name = stage[0]
   data = {'weather':{'pressure':0},'wind':{},'rain':{'1h':0},'extra':{}}
   ret[name] = {'ts':int(datetime.fromisoformat(measure['validTime'].replace("Z", "+00:00")).timestamp()),'timestring':measure['validTime'],'data':data}
   for p in measure['parameters']:
    tp =  xlate.get(p['name'])
    if tp:
     data[tp[1]][tp[0]] = p['values'][0]
   data['extra']['cloud_cover'] = int(data['extra']['cloud_cover'] * 12.5)

  ret['forecast_hours'] = config.get('forecasting',12)
  ret['status'] = 'OK'
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
 return {'status':'OK','code':0,'output':""}

#
#
def parameters(aRT, aArgs):
 """ Function provides parameter mapping of anticipated config vs actual

 Args:

 Output:
  - status
  - parameters
 """
 settings = aRT.config['services'].get('smhi',{})
 params = ['measurement','bucket','longitude','latitude','forecasting']
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}

#
#
def start(aRT, aArgs):
 """ Function provides start behavior

 Args:

 Output:
  - status
 """
 ret = {}
 state = aRT.cache.get('smhi',{})
 if state.get('status') == 'active':
  ret['status'] = 'NOT_OK'
  ret['info'] = 'active'
 else:
  ret['status'] = 'OK'
  ret['info'] = 'scheduled_smhi'
  config = aRT.config['services']['smhi']
  aRT.schedule_api_periodic(process,'smhi_process',3600, args = aArgs, output = aRT.debug)
  aRT.cache['smhi'] = {'status':'active'}
 return ret

#
#
def stop(aRT, aArgs):
 """ Function provides stop behavior

 Args:

 Output:
  - status
 """
 return {'status':'NO OP'}

#
#
def close(aRT, aArgs):
 """ Function provides closing behavior, wrapping up data and file handlers before closing

 Args:

 Output:
  - status
 """
 return {'status':'NO OP'}
