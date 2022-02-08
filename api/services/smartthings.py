"""Smartthings API module. Implements logics to reuse scheduler and influxdb handler for Smartthings statistics """
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "TELEMETRY"

#
#
def report(aCTX, aArgs):
 """ Function report Smartthings data to influxDB

 Args:
  - records. List of records to enter

 Output:
  - status
 """
 records = aArgs['records']
 aCTX.influxdb.write(records, aCTX.config['services']['smartthings']['bucket'])
 return {'status':'OK','function':'smartthings_report','reported':len(records)}

#
#
def process(aCTX, aArgs):
 """Function checks smartthings API, process data and queue reporting to influxDB bucket

 Args:

 Output:
  - status
 """
 from datetime import datetime

 ret = {'function':'smartthings_process'}
 url = 'https://api.smartthings.com/v1/devices/{0}/status'
 hdr = {'Authorization': 'Bearer {0}'.format(aCTX.config['services']['smartthings']['token'])}
 tmpl = 'smartthings,host_id=%s,host_label=%s %s {0}'.format(int(datetime.now().timestamp()))
 state = aCTX.cache.get('smartthings')
 xlate = aCTX.config['services']['smartthings']['capabilities']
 records = []
 if not state:
  # from rims.api.services.smartthings import sync
  state = sync(aCTX, {})['data']
 for id,dev in state['devices'].items():
  try:
   res = aCTX.rest_call(url.format(id), aHeader = hdr, aDataOnly = True, aMethod = 'GET')
  except Exception as e:
   state['sync'] = ret['status'] = 'NOT_OK'
   ret['info'] = str(e)
   break
  else:
   tagvalue = []
   for cap, measure in res['components']['main'].items():
    if cap in dev[0]:
     value = measure[xlate[cap]]['value']
     if isinstance(value, str):
      if value == 'active':
       value = 1
      else:
       value = 0
     elif value is None:
      value = 0
     tagvalue.append("%s=%s"%(xlate[cap],value))
   label = dev[1].replace(" ", "_").replace("/", "-").replace(":", "").lower()
   records.append(tmpl%(id,label,",".join(tagvalue)))
  ret['status'] = 'OK'
 aCTX.queue_api(report,{'records':records}, aOutput = aCTX.debug)
 #report(aCTX,{'records':records})
 return ret

#
#
def device(aCTX, aArgs):
 """Function returns capabilities of a device ID

 Args:
  - device_id (required)

 Output:
  - data
 """
 ret = {}
 hdr = {'Authorization': 'Bearer {0}'.format(aCTX.config['services']['smartthings']['token'])}
 try:
  res = aCTX.rest_call('https://api.smartthings.com/v1/devices/{0}/status'.format(aArgs['device_id']), aHeader = hdr, aDataOnly = True, aMethod = 'GET')
 except Exception as e:
  ret['status'] = 'NOT_OK'
  ret['info'] = str(e)
 else:
  ret['status'] = 'OK'
  ret['data'] = res
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
 state = aCTX.cache.get('smartthings')
 if state:
  ret['status'] = state['sync']
  ret['devices'] = state['devices']
  ret['capabilities'] = state['capabilities']
 else:
  ret['state'] = 'NOT_OK'
 return ret

#
#
def sync(aCTX, aArgs):
 """ Re-fetch the device list and reload capabilities/measurements. Saves them into a dictionary with id:(capabilities, label, name)

 Args:
  - id (required). Server id on master node

 Output:
  - code. (error code, optional)
  - output. (output from command)
  - status. (operation result)
 """
 state = aCTX.cache.get('smartthings',{})
 state['capabilities'] = state_capabilities = {}
 state['devices'] = state_devices = {}
 ret = {}
 url = 'https://api.smartthings.com/v1/devices'
 hdr = {'Authorization': 'Bearer {0}'.format(aCTX.config['services']['smartthings']['token'])}
 try:
  data = aCTX.rest_call(url,aHeader = hdr, aDataOnly = True, aMethod = 'GET')
 except Exception as e:
  state['sync'] = ret['status'] = 'NOT_OK'
  ret['info'] = str(e)
 else:
  capabilities = aCTX.config['services']['smartthings']['capabilities']
  for device in data['items']:
   caps = []
   # Does the device carry any interesting capability?
   for cap in device['components'][0]['capabilities']:
    state_capabilities[cap['id']] = device['deviceId']
    if cap['id'] in capabilities:
     caps.append(cap['id'])
   if caps:
    state_devices[device['deviceId']] = (caps,device['label'],device['name'])
  ret['data'] = state
  state['sync'] = ret['status'] = 'OK'
  aCTX.cache['smartthings'] = state
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
 state = aCTX.cache.get('smartthings',{})
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
 settings = aCTX.config['services'].get('smartthings',{})
 params = ['token','bucket','capabilities']
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}

#
#
def start(aCTX, aArgs):
 """ Function provides start behavior

 Args:

 Output:
  - status
 """
 return {'status':'NO OP'}

#
#
def stop(aCTX, aArgs):
 """ Function provides stop behavior

 Args:

 Output:
  - status
 """
 return {'status':'NO OP'}

