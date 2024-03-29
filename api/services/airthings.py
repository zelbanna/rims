"""Airthings API module. Implements logics to use scheduler and influxdb handler for Airthings statistics

State machine updates phase variable to represent state ok token, always schedule a thread for this - but maybe not use it (because we then cover refresh token in the same start call)
'auth': None -> 'invalid' <-> 'valid'
'running': None -> [True | False]

'state': keep track of names and S/N for data gathering

{
  "module":"services.airthings",
  "function":"start"
},
"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "TELEMETRY"

from core.common import basic_auth
from time import time, sleep

#
#
def auth(aRT, aArgs):
 """ Function provides basic authentication and returns data on success for Oauth2 Client credentials flow. There is no refresh token involved so auth has to be called periodically to populate the state

 Args:

 Output:
  - status
  - data
 """
 state = aRT.cache['airthings']
 config = aRT.config['services']['airthings']
 auth_url = 'https://accounts-api.airthings.com/v1/token'
 header = {'Content-Type':'application/x-www-form-urlencoded'}
 header.update(basic_auth(config['client_id'],config['client_secret']))
 try:
  res = aRT.rest_call(auth_url, aSSL = aRT.ssl, aArgs = {'grant_type':'client_credentials','scope':'read:device:current_values'}, aHeader = header, aMethod = 'POST')
 except Exception as e:
  state.update({'access_token':None,'expires_at':0,'expires_in':0})
  return {'status':'NOT_OK','info':str(e)}
 else:
  state.update({'access_token':res['access_token'],'expires_at':int(time()) + res['expires_in'],'expires_in':res['expires_in']})
  aRT.log(f"airthings_service_authentication successful, expire in {res['expires_in']} seconds")
  return {'status':'OK','data':res}

#
#
def get(aRT, aArgs):
 """ Function provides a generic GET call for the airthings API. since there is only v1 api this info must be omitted in the 'api' argument

 Args:
  - api (required). URI for request
  - debug (optional). Default False

 Output:
 """
 ret = {}
 state = aRT.cache.get('airthings',{})
 url = 'https://ext-api.airthings.com/v1/{0}'.format(aArgs['api'])
 hdr = {'Authorization': 'Bearer %s'%state['access_token']}
 try:
  res = aRT.rest_call(url, aSSL = aRT.ssl, aHeader = hdr, aDebug = aArgs.get('debug',False), aMethod = 'GET')
 except Exception as e:
  ret['status'] = 'NOT_OK'
  ret['info'] = str(e)
 else:
  ret['data'] = res
  ret['status'] = 'OK'
 return ret

#
#
def process(aRT, aArgs):
 """Function checks airthings API, process data and queue reporting to influxDB bucket

 Args:

 Output:
  - status
 """
 state = aRT.cache.get('airthings',{})
 config = aRT.config['services']['airthings']
 tmpl = 'sensor__%s,origin=airthings,system_id=%s,entity_id=%s value=%s %s'
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
   res = aRT.rest_call(f"https://ext-api.airthings.com/v1/devices/{dev['id']}/latest-samples", aSSL = aRT.ssl, aHeader = {'Authorization': 'Bearer %s'%state['access_token']}, aMethod = 'GET')
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
   for k,v in res['data'].items():
    records.append( tmpl%( state['translate'].get(k,k), dev['id'], dev['label'],v,ts))

 if records:
  aRT.influxdb.write(records, config['bucket'])

 return ret

################################################
#
#
def status(aRT, aArgs):
 """Function check cache state and auth status

 Args:
  - type (required)

 Output:
  - data
 """
 state = aRT.cache.get('airthings',{})
 if not state:
  return {'status':'NOT_OK','info':'no_state'}
 elif state.get('expires_at'):
  remaining = state['expires_at'] - int(time())
  if remaining > 0:
   return {'status':'OK','state':state,'remaining':remaining}
  else:
   return {'status':'NOT_OK','info':'token_expired'}
 else:
  return {'status':'NOT_OK','info':'no_synced_state'}

#
#
def sync(aRT, aArgs):
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
 state = aRT.cache.get('airthings',{})
 if not state:
  aRT.cache['airthings'] = state

 res = auth(aRT, aArgs)
 if not res['status'] == 'OK':
  ret['status'] = 'NOT_OK'
  ret['info'] = 'no_state_refresh_impossible'
  ret['output'] = res['info']
  timeout = 60
 else:
  # Authentication done, now ask for devices w S/N and names in lower case - but not too fast
  sleep(10)
  state['translate'] = {
   'temp':'temperature',
   'radonShortTermAvg':'radon'
  }
  try:
   res = aRT.rest_call('https://ext-api.airthings.com/v1/devices', aSSL = aRT.ssl, aHeader = {'Authorization': 'Bearer %s'%state['access_token']}, aDebug = aArgs.get('debug',False), aMethod = 'GET')
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
  aRT.schedule_api(sync,'airthings_token_state_refresh', timeout, args = aArgs, output = aRT.debug)
  ret['function'] = 'airthings_token_state_sync'
  ret['timeout'] = timeout
 return ret

#
#
def restart(aRT, aArgs):
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
def parameters(aRT, aArgs):
 """ Function provides parameter mapping of anticipated config vs actual

 Args:

 Output:
  - status
  - parameters
 """
 settings = aRT.config['services'].get('airthings',{})
 params = ['client_id','client_secret','bucket']
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}

#
#
def start(aRT, aArgs):
 """ Function provides start behavior

 Args:

 Output:
  - status
 """
 ret = {'status':'NOT_OK'}
 config = aRT.config['services']['airthings']

 state = aRT.cache.get('airthings',{})
 if not state:
  aRT.cache['airthings'] = state

 if state.get('running') == None:
  state['running'] = aArgs['schedule'] = True
  sync(aRT, aArgs)
  aRT.schedule_api_periodic(process,'airthings_process',int(config.get('frequency',60)), args = aArgs, output = aRT.debug)
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
def stop(aRT, aArgs):
 """ Function provides stop behavior

 Args:

 Output:
  - status
 """
 state = aRT.cache.get('airthings',{})
 if not state:
  return {'status':'OK','info':'empty_state'}
 elif state.get('running') == None:
  return {'status':'OK','info':'no_running_state'}
 else:
  state['running'] = False
  return {'status':'OK','info':'stopped'}


#
#
def close(aRT, aArgs):
 """ Function provides closing behavior, wrapping up data and file handlers before closing

 Args:

 Output:
  - status
 """
 return {'status':'NO OP'}
