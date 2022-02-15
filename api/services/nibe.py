"""Nibe API module. Implements logics to reuse scheduler and influxdb handler for Nibe statistics """
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "TELEMETRY"

#
#
def initiate(aCTX, aArgs):
 """ Function returns call string

 Args:

 Output: callstring
 """
 from urllib.parse import quote_plus
 state = aCTX.cache.get('nibe',{})
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
 aCTX.cache['nibe'] = state
 code = aArgs['code'][0]
 if state.get('code') == code:
  ret['status'] = 'NOT_OK'
  ret['info'] = 'already authenticated using that code'
 else:
  # from rims.core.common import RestException
  state['phase'] = 'authorize'
  config = aCTX.config['services']['nibe']
  args = {"grant_type":"authorization_code", "client_id":config['client_id'], "client_secret":config['client_secret'],"redirect_uri":config['redirect_uri'],"scope":"READSYSTEM","code":code}
  try:
   res = aCTX.rest_call("https://api.nibeuplink.com/oauth/token", aDataOnly = True, aVerify = False, aArgs = args, aHeader = {'Content-Type':'application/x-www-form-urlencoded'})
  except Exception as e:
   state['phase'] = None
   ret['status'] = 'NOT_OK'
   ret['info'] = str(e)
  else:
   from json import dump
   state['phase'] = 'active'
   state.update(res['data'])
   ret['state'] = state
   # Prep date so that we know when to refresh token

   #
   try:
    with open(config['token_file'],'w+') as file:
     dump(state,file,indent=4)
   except Exception as e:
    ret['token_file'] = str(e)
 return ret

#
#
def refresh(aCTX, aArgs):
 """ Function provides token refresh capabilities

 Args:

 Output:
  - status
 """
 return {'status':'OK'}

#
#
def report(aCTX, aArgs):
 """ Function report Nibe Uplink data to influxDB

 Args:
  - records. List of records to enter

 Output:
  - status
 """
 records = aArgs['records']
 aCTX.influxdb.write(records, aCTX.config['services']['nibe']['bucket'])
 return {'status':'OK','function':'nibe_report','reported':len(records)}

#
#
def process(aCTX, aArgs):
 """Function checks nibe API, process data and queue reporting to influxDB bucket

 Args:

 Output:
  - status
 """
 from datetime import datetime

 ret = {'function':'nibe_process'}
 tmpl = 'smartthings,host_id=%s,host_label=%s %s {0}'.format(int(datetime.now().timestamp()))
 url = 'https://api.smartthings.com/v1/devices/{0}/status'
 hdr = {'Authorization': 'Bearer {0}'.format(aCTX.config['services']['nibe']['token'])}
 try:
  res = aCTX.rest_call(url.format(id), aHeader = hdr, aDataOnly = True, aMethod = 'GET')
 except Exception as e:
  state['sync'] = ret['status'] = 'NOT_OK'
  ret['info'] = str(e)
 else:
  pass
 #aCTX.queue_api(report,{'records':records}, aOutput = aCTX.debug)
 #report(aCTX,{'records':records})
 return ret

################################################
#
#
def status(aCTX, aArgs):
 """Function does a simple smartthings check to verify working connectivity

 Args:
  - type (required)

 Output:
  - data
 """
 ret = {}
 state = aCTX.cache.get('nibe',{})
 aCTX.cache['nibe'] = state
 if state:
  ret['status'] = "OK"
  ret['data'] = state
 else:
  ret['status'] = 'NOT_OK'
 return ret

#
#
def sync(aCTX, aArgs):
 """ Function inititates Oauth process

 Args:
  - id (required). Server id on master node

 Output:
  - code. (error code, optional)
  - output. (output from command)
  - status. (operation result)
 """
 res = refresh(aCTX,{})
 return {'status':res['status'],'code':0,'output':"NO_OP"}

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
 return {'status':'OK','code':0,'output':"NO_OP"}

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
 return initiate(aCTX,{})

#
#
def stop(aCTX, aArgs):
 """ Function provides stop behavior

 Args:

 Output:
  - status
 """
 aCTX.cache['nibe'] = {}
 return {'status':'OK','info':'empty state'}

