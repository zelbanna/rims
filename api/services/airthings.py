"""Airthings API module. Implements logics to use scheduler and influxdb handler for Airthings statistics

State machine updates phase variable to represent state ok token, always schedule a thread for this - but maybe not use it (because we then cover refresh token in the same start call)
'auth': None -> 'invalid' <-> 'valid'
'running': None -> [True | False]

'state': keep track of names and S/N for data gathering

"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "TELEMETRY"

#
#
def auth(aCTX, aArgs):
 """ Function provides basic authentication and returns data on success for Oauth2 Client credentials flow. There is no refresh token involved so auth has to be called periodically to populate the state

 Args:

 Output:
  - status
  - data
 """
 from core.common import basic_auth
 state = aCTX.cache['airthings']
 config = aCTX.config['services']['airthings']
 auth_url = 'https://accounts-api.airthings.com/v1/token'
 header = {'Content-Type':'application/x-www-form-urlencoded'}
 header.update(basic_auth(config['client_id'],config['client_secret']))
 try:
  res = aCTX.rest_call(auth_url, aSSL = aCTX.ssl, aArgs = {'grant_type':'client_credentials','scope':'read:device:current_values'}, aHeader = header, aMethod = 'POST')
 except Exception as e:
  state.update({'access_token':None,'expires_at':0,'expires_in':0})
  return {'status':'NOT_OK','info':str(e)}
 else:
  from time import time
  state.update({'access_token':res['access_token'],'expires_at':int(time()) + res['expires_in'],'expires_in':res['expires_in']})
  aCTX.log(f"airthings_service_authentication successful, expire in {res['expires_in']} seconds")
  return {'status':'OK','data':res}

#
#
def get(aCTX, aArgs):
 """ Function provides a generic GET call for the airthings API. since there is only v1 api this info must be omitted in the 'api' argument

 Args:
  - api (required). URI for request
  - debug (optional). Default False

 Output:
 """
 ret = {}
 state = aCTX.cache.get('airthings',{})
 url = 'https://ext-api.airthings.com/v1/{0}'.format(aArgs['api'])
 hdr = {'Authorization': 'Bearer %s'%state['access_token']}
 try:
  res = aCTX.rest_call(url, aSSL = aCTX.ssl, aHeader = hdr, aDebug = aArgs.get('debug',False), aMethod = 'GET')
 except Exception as e:
  ret['status'] = 'NOT_OK'
  ret['info'] = str(e)
 else:
  ret['data'] = res
  ret['status'] = 'OK'
 return ret

#
#
def process(aCTX, aArgs):
 """Function checks airthings API, process data and queue reporting to influxDB bucket

 Args:

 Output:
  - status
 """
 state = aCTX.cache.get('airthings',{})
 config = aCTX.config['services']['airthings']
 tmpl = '{0},origin=airthings,type=iot,system_id=%s,label=%s %s %s'.format(config.get('measurement','airthings'))
 from time import time
 timestamp = int(time())

 if not state:
  return {'status':'NOT_OK','function':'airthings_process','info':'no_state'}
 elif not state.get('running'):
  return {'status':'NOT_OK','function':'airthings_process','info':'not_running'}
 elif not state['access_token'] or timestamp > state['expires_at']:
  return {'status':'NOT_OK','function':'airthings_process','info':'token_expired'}
 ret = {'status':'OK', 'function':'airthings_process'}
 records = []
 for dev in state.get('devices',[]):
  try:
   res = aCTX.rest_call(f"https://ext-api.airthings.com/v1/devices/{dev['id']}/latest-samples", aSSL = aCTX.ssl, aHeader = {'Authorization': 'Bearer %s'%state['access_token']}, aMethod = 'GET')
  except Exception as e:
   ret['status'] = 'NOT_OK'
   ret['info'] = str(e)
   break
  else:
   # Assume time exists..
   ts = res['data'].pop('time',None)
   if not ts:
    ts = timestamp
   res['data'].pop('relayDeviceType',None)
   records.append( tmpl%( dev['id'], dev['label'], ','.join(["%s=%s"%(state['translate'].get(k,k),v) for k,v in res['data'].items()]), ts))

 if records:
  aCTX.influxdb.write(records, config['bucket'])

 return ret

################################################
#
#
def status(aCTX, aArgs):
 """Function check cache state and auth status

 Args:
  - type (required)

 Output:
  - data
 """
 state = aCTX.cache.get('airthings',{})
 if not state:
  return {'status':'NOT_OK','info':'no_state'}
 elif state.get('expires_at'):
  from time import time
  remaining = state['expires_at'] - int(time())
  if remaining > 0:
   return {'status':'OK','state':state,'remaining':remaining}
  else:
   return {'status':'NOT_OK','info':'token_expired'}
 else:
  return {'status':'NOT_OK','info':'no_synced_state'}

#
#
def sync(aCTX, aArgs):
 """ Function refresh Oauth token, essentially call for a new one and populate the state tables

 Args:
  - id (required). Server id on master node
  - schedule (optional). default False

 Output:
  - code. (error code, optional)
  - output. (output from command)
  - status. (operation result)
 """
 ret = {}
 state = aCTX.cache.get('airthings',{})
 if not state:
  aCTX.cache['airthings'] = state

 res = auth(aCTX, aArgs)
 if not res['status'] == 'OK':
  ret['status'] = 'NOT_OK'
  ret['info'] = 'no_state_refresh_impossible'
  ret['output'] = res['info']
  timeout = 60
 else:
  # Authentication done, now ask for devices w S/N and names in lower case - but not too fast
  from time import sleep
  sleep(10)
  state['translate'] = {
   'temp':'temperature',
   'radonShortTermAvg':'radon'
  }
  try:
   res = aCTX.rest_call('https://ext-api.airthings.com/v1/devices', aSSL = aCTX.ssl, aHeader = {'Authorization': 'Bearer %s'%state['access_token']}, aDebug = aArgs.get('debug',False), aMethod = 'GET')
  except Exception as e:
   timeout = 60
   ret['status'] = 'NOT_OK'
   ret['info'] = 'no_data_response'
   ret['extra'] = str(e)
  else:
   ret['status'] = 'OK'
   state['devices'] = [{'id':dev['id'],'location':dev['location']['name'],'label':dev['segment']['name'].replace(" ", "_").replace("/", "-").replace(":", "").lower()} for dev in res['devices']]
   timeout = state['expires_in'] - 5

 if aArgs.get('schedule'):
  aCTX.schedule_api(sync,'airthings_token_state_refresh', timeout, args = aArgs, output = aCTX.debug)
  ret['function'] = 'airthings_token_state_sync'
  ret['timeout'] = timeout
 return ret

#
#
def restart(aCTX, aArgs):
 """Function reload Oauth state

 Args:
  - id (required). Server id on master node

 Output:
  - code
  - output
  - result 'OK'/'NOT_OK'
 """
 return {'status':'NOT_OK','info':'not_implemented'}

#
#
def parameters(aCTX, aArgs):
 """ Function provides parameter mapping of anticipated config vs actual

 Args:

 Output:
  - status
  - parameters
 """
 settings = aCTX.config['services'].get('airthings',{})
 params = ['client_id','client_secret','bucket']
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}

#
#
def start(aCTX, aArgs):
 """ Function provides start behavior

 Args:

 Output:
  - status
 """
 ret = {'status':'NOT_OK'}
 config = aCTX.config['services']['airthings']

 state = aCTX.cache.get('airthings',{})
 if not state:
  aCTX.cache['airthings'] = state

 if state.get('running') == None:
  state['running'] = aArgs['schedule'] = True
  sync(aCTX, aArgs)
  aCTX.schedule_api_periodic(process,'airthings_process',int(config.get('frequency',60)), args = aArgs, output = aCTX.debug)
  ret['status'] = 'OK'
  ret['info'] = 'scheduled_airthings'
 elif state['running']:
  ret['info'] = 'running'
 else:
  state['running'] = True
  ret['status'] = 'OK'
 return ret

#
#
def stop(aCTX, aArgs):
 """ Function provides stop behavior

 Args:

 Output:
  - status
 """
 state = aCTX.cache.get('airthings',{})
 if not state:
  return {'status':'OK','info':'empty_state'}
 elif state.get('running') == None:
  return {'status':'OK','info':'no_running_state'}
 else:
  state['running'] = False
  return {'status':'OK','info':'stopped'}


#
#
def close(aCTX, aArgs):
 """ Function provides closing behavior, wrapping up data and file handlers before closing

 Args:

 Output:
  - status
 """
 return {'status':'NO OP'}
