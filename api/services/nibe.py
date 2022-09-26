"""Nibe API module. Implements logics to use scheduler and influxdb handler for Nibe statistics

State machine updates phase variable to represent state ok token, always schedule a thread for this - but maybe not use it (because we then cover refresh token in the same start call)
'phase': None -> init (bootstrap) -> authorize -> [invalid -> refresh -> valid]
'running': None -> [True | False]

"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "TELEMETRY"

from urllib.parse import quote_plus
from time import time
from json import dump, load

#
#
def bootstrap(aCTX, aArgs):
 """ Function provides start behavior, i.e. bootstrap authentication and token handling process

 Args:

 Output:
  - status
 """
 state = aCTX.cache.get('nibe',{})
 if not state:
  aCTX.cache['nibe'] = state
 state['phase'] = 'init'
 config = aCTX.config['services']['nibe']
 redirect_uri = quote_plus(config['redirect_uri'])
 return {"status":"OK", "callstring":f"https://api.nibeuplink.com/oauth/authorize?response_type=code&client_id={config['client_id']}&scope=READSYSTEM&redirect_uri={redirect_uri}&state={config['state']}"}

#
#
def auth(aCTX, aArgs):
 """ Function is callback URI for phase one Oauth 2.0 authentication

 Args:
  - code (required)
  - state (required)

 Output:
 """
 ret = {}
 state = aCTX.cache.get('nibe',{})
 if not state:
  aCTX.cache['nibe'] = state
 code = aArgs['code'][0]
 if state.get('code') == code:
  ret['status'] = 'NOT_OK'
  ret['info'] = 'already authenticated using that code'
 else:
  state['phase'] = 'authorize'
  config = aCTX.config['services']['nibe']
  args = {"grant_type":"authorization_code", "client_id":config['client_id'], "client_secret":config['client_secret'],"redirect_uri":config['redirect_uri'],"scope":"READSYSTEM","code":code}
  try:
   res = aCTX.rest_call("https://api.nibeuplink.com/oauth/token", aSSL = aCTX.ssl, aArgs = args, aHeader = {'Content-Type':'application/x-www-form-urlencoded'})
  except Exception as e:
   state['phase'] = None
   ret['status'] = 'NOT_OK'
   ret['info'] = str(e)
   aCTX.log(f"nibe_service_authentication phase 1 NOT successful")
  else:
   state.update({'access_token':res['access_token'],'refresh_token':res['refresh_token'],'phase':'valid','expires_at':int(time()) + res['expires_in'],'expires_in':res['expires_in']})
   ret['status'] = 'OK'
   try:
    with open(config['token_file'],'w+') as file:
     dump(state,file,indent=4)
   except Exception as e:
    ret['token_file_error'] = str(e)
   aCTX.log(f"nibe_service_authentication successful, expire in {res['expires_in']} seconds")
 return ret

#
#
def process(aCTX, aArgs):
 """Function checks nibe API, process data and queue reporting to influxDB bucket

 Args:

 Output:
  - status
 """
 timestamp = int(time())
 state = aCTX.cache.get('nibe',{})

 if not state:
  return {'status':'NOT_OK','function':'nibe_process','info':'no_state'}
 elif not state.get('running'):
  return {'status':'NOT_OK','function':'nibe_process','info':'not_running'}
 elif state['phase'] != 'valid' or timestamp > state['expires_at']:
  return {'status':'NOT_OK','function':'nibe_process','info':'token_expired'}

 scaling = {10001:1,10012:1,10033:1,43084:0.1,43416:1,43420:1,43424:1}
 mapping = {"\u00b0C":"temperature","kW":"power","A":"current","%":"load","h":"elapsed_time"}
 ret = {'status':'OK','function':'nibe_process'}
 config = aCTX.config['services']['nibe']
 sys_id = config['system_id']
 tmpl = '{0},origin=nibe,type=heater,system_id={1},parameter=%s,designation=%s,label=%s %s=%s {2}'.format(config.get('measurement','nibe'),sys_id,timestamp)
 url = f'https://api.nibeuplink.com/api/v1/systems/{sys_id}/serviceinfo/categories/%s'

 def __check_call(aParam):
  items = aCTX.rest_call(url%aParam, aHeader = hdr, aSSL = aCTX.ssl, aMethod = 'GET')
  parameters.update({v['parameterId']:v for v in items})

 hdr = {'Authorization': f"Bearer {state['access_token']}"}
 try:
  parameters = {}
  aCTX.queue_block(__check_call,["STATUS","CPR_INFO_EP14","SYSTEM_1","ADDITION","VENTILATION"])
 except Exception as e:
  ret['status'] = 'NOT_OK'
  ret['info'] = str(e)
 else:
  records = []
  for x in [40067,40071,43161,47212,47214]:
   parameters.pop(x,None)
  for k,v in parameters.items():
   label = v['title'].replace(" ", "_").replace("/", "-").replace(":", "").replace(".", "").lower()
   records.append(tmpl%(k, v['designation'] if v['designation'] else k, label, mapping.get(v['unit'],"unit"), v['rawValue']/scaling.get(k,10) ))
  aCTX.influxdb.write(records, config['bucket'])
 return ret

#
#
def get(aCTX, aArgs):
 """ Function provides a generic GET call for the nibe API. since there is only v1 api this info must be omitted in the 'api' argument

 Args:
  - api (required). URI for request
  - debug (optional). Default False

 Output:
 """
 ret = {}
 state = aCTX.cache.get('nibe',{})
 url = 'https://api.nibeuplink.com/api/v1/{0}'.format(aArgs['api'])
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
 ret = None
 state = aCTX.cache.get('nibe',{})
 if not state:
  aCTX.cache['nibe'] = state
 if state:
  remaining = state['expires_at'] - int(time())
  if remaining > 0:
   ret = {'status':'OK','state':state,'remaining':remaining}
  else:
   ret = {'status':'NOT_OK','info':'token_expired'}
 else:
  ret = {'status':'NOT_OK','info':'no_state'}
 return ret

#
#
def sync(aCTX, aArgs):
 """ Function refresh Oauth token

 Args:
  - id (required). Server id on master node
  - schedule (optional). default False

 Output:
  - code. (error code, optional)
  - output. (output from command)
  - status. (operation result)
 """
 ret = {}
 state = aCTX.cache.get('nibe',{})
 if not state:
  state['phase'] = 'invalid'
  ret['status'] = 'NOT_OK'
  ret['info'] = 'no_state_refresh_impossible'
  aCTX.log(f"nibe_service_token_refresh phase 2 impossible")
 else:
  state['phase'] = 'refresh'
  config = aCTX.config['services']['nibe']
  args = {"grant_type":"refresh_token", "client_id":config['client_id'], "client_secret":config['client_secret'],"refresh_token":state['refresh_token']}
  try:
   res = aCTX.rest_call("https://api.nibeuplink.com/oauth/token", aSSL = aCTX.ssl, aArgs = args, aHeader = {'Content-Type':'application/x-www-form-urlencoded'})
  except Exception as e:
   state['phase'] = 'invalid'
   ret['status'] = 'NOT_OK'
   ret['info'] = str(e)
   aCTX.log(f"nibe_service_token_refresh phase 2 NOT successful")
  else:
   state.update({'access_token':res['access_token'],'refresh_token':res['refresh_token'],'phase':'valid','expires_at':int(time()) + res['expires_in'],'expires_in':res['expires_in']})
   ret['status'] = 'OK'
   try:
    with open(config['token_file'],'w+') as file:
     dump(state,file,indent=4)
   except Exception as e:
    ret['token_file_error'] = str(e)
   aCTX.log(f"nibe_service_token_refresh successful, expire in {res['expires_in']} seconds")
   ret['output'] = res['expires_in']
  finally:
   if aArgs.get('schedule'):
    aCTX.schedule_api(sync,'nibe_token_refresh', state['expires_in'], args = aArgs, output = aCTX.debug)
    ret['function'] = 'nibe_token_sync'

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
 ret = {}
 config = aCTX.config['services']['nibe']
 try:
  with open(config['token_file'],'r') as file:
   state = aCTX.cache['nibe'] = load(file)
 except Exception as e:
  ret['output'] = str(e)
  ret['status'] = 'NOT_OK'
 else:
  ret['remaining'] = state['expires_at'] - int(time())
  ret['status'] = 'OK'
 return ret

#
#
def parameters(aCTX, aArgs):
 """ Function provides parameter mapping of anticipated config vs actual

 Args:

 Output:
  - status
  - parameters
 """
 settings = aCTX.config['services'].get('nibe',{})
 params = ['client_id','client_secret','redirect_uri','bucket','token_file','state']
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
 config = aCTX.config['services']['nibe']
 state = aCTX.cache.get('nibe')
 if not state:
  # Get phase but forget about running state
  try:
   with open(config['token_file'],'r') as file:
    state = aCTX.cache['nibe'] = load(file)
  except Exception as e:
   return {'output':str(e),'status':'NOT_OK'}
  else:
   state['running'] = None

 if state['phase'] == 'valid':
  # Phase is ok - we can start all the scheduling...
  if state.get('running') == None:
   remaining = state['expires_at'] - int(time())
   state['running'] = aArgs['schedule'] = True
   if remaining > 0:
    aCTX.schedule_api(sync,'nibe_token_refresh',remaining, args = aArgs, output = aCTX.debug)
   else:
    sync(aCTX, aArgs)
   aCTX.schedule_api_periodic(process,'nibe_process',int(config.get('frequency',60)), args = aArgs, output = aCTX.debug)
   ret['info'] = 'scheduled_nibe'
   ret['status'] = 'OK'
  elif state['running']:
   ret['info'] = 'running'
  else:
   state['running'] = True
   ret['status'] = 'OK'
 else:
  ret['info'] = 'phase_not_ok'
 return ret

#
#
def stop(aCTX, aArgs):
 """ Function provides stop behavior

 Args:

 Output:
  - status
 """
 state = aCTX.cache.get('nibe',{})
 if not state:
  aCTX.cache['nibe'] = state
 if state.get('running') == None:
  return {'status':'OK','info':'empty state'}
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
