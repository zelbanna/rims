"""OpenWeatherMap API module. Implements logics to reuse scheduler and influxdb handler for OpenWeatherMap weather data """
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "TELEMETRY"

#
#
def process(aRT, aArgs):
 """Function checks OpenWeathermap API, process data and queue reporting to influxDB bucket

 Args:

 Output:
  - status
 """
 ret = {'status':'OK','function':'openweathermap_process'}
 state = aRT.cache.get('openweathermap',{'status':'forced','timestamp':0})
 if state['status'] != 'inactivate':
  config = aRT.config['services']['openweathermap']
  res = sync(aRT,None)
  if res['status'] == 'OK' and res['data']['dt'] > state['timestamp']:
   data = res['data']
   ts = state['timestamp'] = data['dt']
   tmpl = '{0},origin=openweathermap,type=weather,system_id={1},label=%s %s {2}'.format(config.get('measurement','openweathermap'),data['id'],ts)
   records = [tmpl%('weather',",".join("%s=%s"%(k,v) for k,v in data['main'].items()))]
   records.append(tmpl%('wind',",".join("%s=%s"%(k,v) for k,v in data['wind'].items())))
   records.append(tmpl%('air',",".join("%s=%s"%(k,v) for k,v in data['air'].items())))
   records.append(tmpl%('extra',f"clouds={data['clouds']['all']},visibility={data['visibility'] / 1000}"))
   records.append(tmpl%('rain',f"rain={data.get('rain',{'1h':0})['1h']}"))
   if state['status'] == 'active':
    aRT.influxdb.write(records, config['bucket'])
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
def sync(aRT, aArgs):
 """Function does a check and returns status of the service

 Args:
  - id (required)

 Output:
  - data
  - status
 """
 ret = {}
 config = aRT.config['services']['openweathermap']
 url = 'https://api.openweathermap.org/data/2.5/%s?lat={latitude}&lon={longitude}&appid={token}&units=metric'.format(**config)
 try:
  res = aRT.rest_call(url%'weather', aSSL = aRT.ssl, aMethod = 'GET')
  air = aRT.rest_call(url%'air_pollution', aSSL = aRT.ssl, aMethod = 'GET')['list'][0]
  res['air'] = air['components']
  res['air']['co2'] = res['air'].pop('co',0)
  res['air']['pm25'] = res['air'].pop('pm2_5',0)
  main = res['main']
  main['air_quality'] = air['main']['aqi']
  main['temperature'] = main.pop('temp',0)
 except Exception as e:
  ret['info'] = str(e)
  ret['status'] = 'NOT_OK'
 else:
  ret['data'] = res
  ret['state'] = aRT.cache.get('openweathermap')
  ret['status'] = 'OK'
 return ret

#
#
def status(aRT, aArgs):
 """ No-Op

 Args:

 Output:
  - status. (operation result)
 """
 ret = {'status':'OK'}
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
 settings = aRT.config['services'].get('openweathermap',{})
 params = ['token','bucket','measurement','longitude','latitude']
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
 state = aRT.cache.get('openweathermap',{})
 if state.get('status') == 'active':
  ret['status'] = 'NOT_OK'
  ret['info'] = 'active'
 else:
  ret['status'] = 'OK'
  ret['info'] = 'scheduled_openweathermap'
  config = aRT.config['services']['openweathermap']
  aRT.schedule_api_periodic(process,'openweathermap_process',int(config.get('frequency',60)), args = aArgs, output = aRT.debug)
  aRT.cache['openweathermap'] = {'status':'active','timestamp':0}
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
