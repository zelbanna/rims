"""Smartthings API module. Implements logics to reuse scheduler and influxdb handler for Smartthings statistics """
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "TELEMETRY"

#
#
def process(aCTX, aArgs):
 """Function checks smartthings API, process data and queue reporting to influxDB bucket

 Args:

 Output:
  - status
 """
 from time import time

 ret = {'status':'OK','function':'smartthings_process'}
 url = 'https://api.smartthings.com/v1/devices/{0}/status'
 config = aCTX.config['services']['smartthings']
 hdr = {'Authorization': 'Bearer {0}'.format(config['token'])}
 tmpl = '{0},origin=smartthings,type=iot,system_id=%s,label=%s %s {1}'.format(config.get('measurement','smartthings'),int(time()))
 records = []
 state = aCTX.cache.get('smartthings')
 if not state:
  # from rims.api.services.smartthings import sync
  res = sync(aCTX, {})
  if res['status'] == 'OK':
   state = res['data']
  else:
   return {'status':'NOT_OK','function':'smartthings_process','info':res['info']}
 xlate = state['translate']
 for id,dev in state['devices'].items():
  try:
   res = aCTX.rest_call(url.format(id), aSSL = aCTX.ssl, aHeader = hdr, aMethod = 'GET')
  except Exception as e:
   state['sync'] = ret['status'] = 'NOT_OK'
   ret['info'] = str(e)
   break
  else:
   tagvalue = []
   for cap, measure in res['components']['main'].items():
    if cap in dev[0]:
     value = measure[xlate[cap][0]]['value']
     if isinstance(value, str):
      value = 1 if value == 'active' else 0
     elif value is None:
      value = 0
     tagvalue.append("%s=%s"%(xlate[cap][1],value))
   records.append(tmpl%(id,dev[1],",".join(tagvalue)))
 aCTX.influxdb.write(records, config['bucket'])
 return ret

#
#
def device(aCTX, aArgs):
 """Function returns capabilities of a device ID

 Args:
  - device (required)

 Output:
  - data
 """
 ret = {}
 hdr = {'Authorization': 'Bearer {0}'.format(aCTX.config['services']['smartthings']['token'])}
 try:
  res = aCTX.rest_call('https://api.smartthings.com/v1/devices/{0}/status'.format(aArgs['device']), aSSL = aCTX.ssl, aHeader = hdr, aMethod = 'GET')
 except Exception as e:
  ret['status'] = 'NOT_OK'
  ret['info'] = str(e)
 else:
  ret['status'] = 'OK'
  ret['data'] = res
 return ret

########################################################################################
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
  ret['status'] = "OK" if state['sync'] else "NOT_OK"
  ret['devices'] = state['devices']
  ret['capabilities'] = state['capabilities']
 else:
  ret['status'] = 'NOT_OK'
 return ret

#
#
def sync(aCTX, aArgs):
 """ Re-fetch the device list and reload capabilities/measurements. Saves them into a dictionary with id:(capabilities, influx label, label, name, room_id)

 Don't filter any capability in the call - so we can list all possible in the status

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
 state['locations'] = state_locs = {}
 state['rooms'] = state_rooms = {}
 state['translate'] = state_xlate = {
  'tvocMeasurement':('tvocLevel','tvoc'),
  'temperatureMeasurement':('temperature','temperature'),
  'relativeHumidityMeasurement':('humidity','humidity'),
  'atmosphericPressureMeasurement':('atmosphericPressure','pressure'),
  'illuminanceMeasurement':('illuminance','illuminance'),
  'battery':('battery','battery'),
  'powerMeter':('power','power'),
  'energyMeter':('energy','energy')
 }
 ret = {}
 devs_url = 'https://api.smartthings.com/v1/devices'
 locs_url = 'https://api.smartthings.com/v1/locations'
 room_url = 'https://api.smartthings.com/v1/locations/{0}/rooms'
 hdr = {'Authorization': 'Bearer {0}'.format(aCTX.config['services']['smartthings']['token'])}
 try:
  devs = aCTX.rest_call(devs_url, aSSL = aCTX.ssl, aHeader = hdr, aMethod = 'GET')
  locs = aCTX.rest_call(locs_url, aSSL = aCTX.ssl, aHeader = hdr, aMethod = 'GET')
  for loc in locs['items']:
   state_locs[loc['locationId']] = loc['name']
   rooms = aCTX.rest_call(room_url.format(loc['locationId']), aSSL = aCTX.ssl, aHeader = hdr, aMethod = 'GET')
   for room in rooms['items']:
    state_rooms[room['roomId']] = room['name']
 except Exception as e:
  state['sync'] = False
  ret['status'] = 'NOT_OK'
  ret['info'] = str(e)
 else:
  for device in devs['items']:
   caps = []
   # Does the device carry any interesting capability?
   for cap in device['components'][0]['capabilities']:
    state_capabilities[cap['id']] = device['deviceId']
    if cap['id'] in state_xlate:
     caps.append(cap['id'])
   if caps:
    room = state_rooms.get(device['roomId'],'unknown')
    label = f"{room}_{device['label']}".replace(" ", "_").replace("/", "-").replace(":", "").lower()
    state_devices[device['deviceId']] = (caps,label,device['label'],device['name'],room)
  state['sync'] = True
  ret['data'] = state
  ret['status'] = 'OK'
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
 state['sync'] = False
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
 config = aCTX.config['services']['smartthings']
 aCTX.schedule_api_periodic(process,'smartthings_process',int(config.get('frequency',60)), args = aArgs, output = aCTX.debug)
 return {'status':'OK','info':'scheduled_smartthings'}

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
