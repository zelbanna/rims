"""OpenWeatherMap API module. Implements logics to reuse scheduler and influxdb handler for OpenWeatherMap weather data """
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "TELEMETRY"

#
#
def process(aCTX, aArgs):
 """Function checks OpenWeathermap API, process data and queue reporting to influxDB bucket

 Args:

 Output:
  - status
 """
 ret = {'status':'OK','function':'openweathermap_process'}
 state = aCTX.cache.get('openweathermap',{'status':'forced','timestamp':0})
 if state['status'] != 'inactivate':
  config = aCTX.config['services']['openweathermap']
  res = status(aCTX,None)
  if res['status'] == 'OK' and res['data']['dt'] > state['timestamp']:
   data = res['data']
   ts = state['timestamp'] = data['dt']
   tmpl = '{0},type=weather,designation=%s,system_id=%s,label=%s %s {1}'.format(config.get('measurement','openweathermap'),ts)
   records = [tmpl%('sys_weather',data['id'],'weather',",".join("%s=%s"%(k,v) for k,v in data['main'].items()))]
   records.append(tmpl%('sys_wind',data['id'],'wind',",".join("%s=%s"%(k,v) for k,v in data['wind'].items())))
   records.append(tmpl%('sys_air',data['id'],'air',",".join("%s=%s"%(k,v) for k,v in data['air'].items())))
   records.append(tmpl%('sys_extra',data['id'],'extra',f"clouds={data['clouds']['all']},visibility={data['visibility'] / 100}"))
   records.append(tmpl%('sys_rain',data['id'],'rain',f"rain={data.get('rain',{'1h':0})['1h']}"))
   if state['status'] == 'active':
    aCTX.influxdb.write(records, config['bucket'])
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
def status(aCTX, aArgs):
 """Function does a check and returns status of the service

 Args:
  - type (required)

 Output:
  - data
 """
 ret = {}
 config = aCTX.config['services']['openweathermap']
 url = 'https://api.openweathermap.org/data/2.5/%s?lat={latitude}&lon={longitude}&appid={token}&units=metric'.format(**config)
 try:
  res = aCTX.rest_call(url%'weather', aSSL = aCTX.ssl, aMethod = 'GET')
  air = aCTX.rest_call(url%'air_pollution', aSSL = aCTX.ssl, aMethod = 'GET')['list'][0]
  res['air'] = air['components']
  main = res['main']
  main['air_quality'] = air['main']['aqi']
  main['atmosphericPressure'] = main.pop('pressure',1) / 10
  main['temperature'] = main.pop('temp',0)
 except Exception as e:
  ret['info'] = str(e)
  ret['status'] = 'NOT_OK'
 else:
  ret['data'] = res
  ret['state'] = aCTX.cache.get('openweathermap')
  ret['status'] = 'OK'
 return ret

#
#
def sync(aCTX, aArgs):
 """ No-Op

 Args:
  - id (required). Server id on master node

 Output:
  - code. (error code, optional)
  - output. (output from command)
  - status. (operation result)
 """
 ret = {'status':'OK'}
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
 return {'status':'OK','code':0,'output':""}

#
#
def parameters(aCTX, aArgs):
 """ Function provides parameter mapping of anticipated config vs actual

 Args:

 Output:
  - status
  - parameters
 """
 settings = aCTX.config['services'].get('openweathermap',{})
 params = ['token','bucket']
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}

#
#
def start(aCTX, aArgs):
 """ Function provides start behavior

 Args:

 Output:
  - status
 """
 ret = {'info':'scheduled_openweathermap'}
 state = aCTX.cache.get('openweathermap',{})
 if state.get('status') == 'activated':
  ret['status'] = 'NOT_OK'
  ret['info'] = 'active'
 else:
  ret['status'] = 'OK'
  config = aCTX.config['services']['openweathermap']
  aCTX.schedule_api_periodic(process,'openweathermap_process',int(config.get('frequency',60)), args = aArgs, output = aCTX.debug)
  aCTX.cache['openweathermap'] = {'status':'activated','timestamp':0}
 return ret

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
def close(aCTX, aArgs):
 """ Function provides closing behavior, wrapping up data and file handlers before closing

 Args:

 Output:
  - status
 """
 return {'status':'NO OP'}
