"""HomeAssistant API module. Implements logics to reuse scheduler and influxdb handler for statistics

- Use 'start' to run scheduled with X frequency

"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "TELEMETRY"

from time import time

#
#
def process(aRT, aArgs):
 """Function checks homeassistant API, process data and queue reporting to influxDB bucket

 Args:

 Output:
  - status
 """
 def is_float(a_string):
  try:
   float(a_string)
   return True
  except ValueError:
   return False

 config = aRT.config['services']['hass']
 url = config['endpoint']
 hdr = {'Authorization': 'Bearer {0}'.format(config['token'])}
 tmpl = '%s,origin=ha,entity_id=%s,friendly_name=%s value=%s {0}'.format(int(time()))

 #####
 try:
  res = aRT.rest_call(url + "/api/states", aHeader = hdr, aMethod = 'GET')
 except Exception as e:
  return {'status':'NOT_OK','info':str(e)}
 else:
  # Start pulling measurements :-)
  data = [dev for dev in res if dev['attributes'].get('unit_of_measurement') and is_float(dev['state'])]
  records = [tmpl%(dev['attributes'].get('device_class','unit'),dev['entity_id'],dev['attributes'].get('friendly_name','None').replace(" ", "_").replace("/", "-").replace(":", "").replace(".", "").lower(), dev['state']) for dev in data]
  aRT.influxdb.write(records, config['bucket'])
  return {'status':'OK','function':'homeassistant_process','records':len(records)}

#
#
def entity(aRT, aArgs):
 """Function does a simple homeassistant entity check

 Args:
  - entity_id (required)

 Output:
  - data
 """
 config = aRT.config['services']['hass']
 url = config['endpoint']
 hdr = {'Authorization': 'Bearer {0}'.format(config['token'])}
 tmpl = '%s,origin=ha,entity_id=%s,friendly_name=%s value=%s {0}'.format(int(time()))
 try:
  res = aRT.rest_call(url + "/api/states/%s"%aArgs['entity_id'], aHeader = hdr, aMethod = 'GET')
 except Exception as e:
  return {'status':'NOT_OK','info':str(e)}
 else:
  # Start pulling measurements :-)
  return {'status':'OK','data':res}

#
#
def states(aRT, aArgs):
 """Function returns homeassistant entites

 Args:

 Output:
  - data
 """
 config = aRT.config['services']['hass']
 url = config['endpoint']
 hdr = {'Authorization': 'Bearer {0}'.format(config['token'])}
 tmpl = '%s,origin=ha,entity_id=%s,friendly_name=%s value=%s {0}'.format(int(time()))
 try:
  res = aRT.rest_call(url + "/api/states", aHeader = hdr, aMethod = 'GET')
 except Exception as e:
  return {'status':'NOT_OK','info':str(e)}
 else:
  # Start pulling measurements :-)
  return {'status':'OK','data':res}

########################################################################################
#
#
def status(aRT, aArgs):
 """Function does a simple homeassistant check to verify working connectivity

 Args:
  - type (required)

 Output:
  - data
 """
 ret = {}
 state = aRT.cache.get('hass')
 if state:
  ret['status'] = "OK" if state['sync'] else "NOT_OK"
  ret['devices'] = state['devices']
  ret['capabilities'] = state['capabilities']
 else:
  ret['status'] = 'NOT_OK'
 return ret

#
#
def sync(aRT, aArgs):
 """
 Args:
  - id (required). Server id on master node

 Output:
  - code. (error code, optional)
  - output. (output from command)
  - status. (operation result)
 """
 return {'status':'NO_OP'}

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
 state = aRT.cache.get('hass',{})
 state['sync'] = False
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
 settings = aRT.config['services'].get('hass',{})
 params = ['token','bucket','capabilities']
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}

#
#
def start(aRT, aArgs):
 """ Function provides start behavior

 Args:

 Output:
  - status
 """
 config = aRT.config['services']['hass']
 aRT.schedule_api_periodic(process,'homeassistant_process',int(config.get('frequency',60)), args = aArgs, output = aRT.debug)
 return {'status':'OK','info':'scheduled_homeassistant'}

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
