"""Huawei Solar SUN2000 API module. Implements logics to reuse scheduler and influxdb handler for connection to Dongle or Internal Modbus endpoint """
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "TELEMETRY"

#
#
def process(aCTX, aArgs):
 """Function checks modbus registers, process data and queue reporting to influxDB bucket

 Args:

 Output:
  - status
 """
 from time import time
 ret = {'status':'OK','function':'sun2000_process'}
 state = aCTX.cache.get('sun2000')
 if state['status'] == 'active':
  config = aCTX.config['services']['sun2000']
  res = sync(aCTX,None)
  if res['status'] == 'OK':
   data = res['data']
   id = data.pop('serial_number',{'value':'N/A'})['value']
   tmpl = '{0},origin=sun2000,type=solar,system_id=%s,label=%s %s=%s {1}'.format(config.get('measurement','sun2000'),int(time()))
   records = [tmpl%(id,k,v['unit'],v['value']) for k,v in data.items()]
   aCTX.influxdb.write(records, config['bucket'])
   if aCTX.debug:
    ret['data'] = records
  else:
   ret = res
 else:
  ret['status'] = 'NOT_OK'
  ret['info'] = 'inactive'
 return ret

#
#
def __init_state(aCTX, aArgs):
 """ Function initialize state for sun2000

 Args:

 Output:
  - status
 """
 config = aCTX.config['services']['sun2000']
 state = aCTX.cache.get('sun2000')
 if not state:
  state = aCTX.cache['sun2000'] = {'status':'inactive'}
 state['mapping'] = {'\u00b0C':'temperature','W':'power','kWh':'energy','A':'current','%':'load','h':'elapsed_time','VA':'VA','V':'volt','Hz':'frequency','Var':'Var'}
 state['singles'] = ['serial_number','accumulated_yield_energy']
 for i in range(1,int(config['n_storage'])+1):
  state['singles'].extend([f'storage_unit_{i}_charge_discharge_power','storage_unit_1_state_of_capacity'])

 strings = ['pv_01_voltage','pv_01_current']
 for i in range(2,int(config['n_strings'])+1):
  strings.extend([f'pv_{i:02d}_voltage',f'pv_{i:02d}_current'])
 system = ['phase_A_voltage','phase_B_voltage','phase_C_voltage','phase_A_current','phase_B_current','phase_C_current','day_active_power_peak','active_power','reactive_power','power_factor','grid_frequency','efficiency','internal_temperature']
 meter = ['power_meter_active_power','power_meter_reactive_power','active_grid_power_factor','active_grid_frequency','grid_exported_energy','grid_accumulated_energy','grid_accumulated_reactive_power']
 state['ranges'] = [strings, system, meter]
 state['items'] = state['singles'].copy()
 state['items'].extend(strings)
 state['items'].extend(system)
 state['items'].extend(meter)
 return state

########################################################################################
#
#
def status(aCTX, aArgs):
 """Function retrives status of service

 Args:
  - type (required)

 Output:
 """
 ret = {}
 config = aCTX.config['services']['sun2000']
 return {'status':'OK','state':aCTX.cache.get('sun2000')}


#
#
def sync(aCTX, aArgs):
 """ Sync data and return register values

 Args:
  - id (required). Server id on master node

 Output:
  - status. (operation result)
 """
 from time import time
 import asyncio
 from huawei_solar import AsyncHuaweiSolar

 config = aCTX.config['services']['sun2000']
 state = aCTX.cache.get('sun2000')
 if not state:
  state = __init_state(aCTX, None)
 loop = asyncio.new_event_loop()

 async def main(con: AsyncHuaweiSolar, mapping: dict, singles: list[str], ranges: list[list[str]], items: list[str]):
  try:
   probes = [con.get_multiple(x) for x in ranges]
   probes.extend([con.get(x) for x in singles])
   output = await asyncio.gather(*probes)
  except Exception as e:
   raise Exception(f'SUN2000 Error: {str(e)}')
  else:
   flatten = output[3:]
   flatten.extend([item for sublist in output[:3] for item in sublist])
   return {items[i]:{'value':r.value,'unit':mapping.get(r.unit,'unit')} for i,r in enumerate(flatten)}

 ret = {}
 try:
  con = loop.run_until_complete(AsyncHuaweiSolar.create(config['ip'],port = config.get('port',6607)))
  data = loop.run_until_complete(main(con,state['mapping'],state['singles'],state['ranges'],state['items']))
  loop.run_until_complete(con.stop())
 except Exception as e:
  ret['status'] = 'NOT_OK'
  ret['info'] = str(e)
 else:
  ret['status'] = 'OK'
  ret['data'] = data
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
 settings = aCTX.config['services'].get('sun2000',{})
 params = ['measurement','bucket','n_strings','n_storage','ip','port']
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}

#
#
def start(aCTX, aArgs):
 """ Function provides start behavior

 Args:

 Output:
  - status
 """
 ret = {'info':'scheduled_sun2000'}
 state = aCTX.cache.get('sun2000',{})
 if state.get('status') == 'active':
  ret['status'] = 'NOT_OK'
  ret['info'] = 'already_active'
 else:
  ret['status'] = 'OK'
  config = aCTX.config['services']['sun2000']
  aCTX.schedule_api_periodic(process,'sun2000_process',int(config.get('frequency',60)), args = aArgs, output = aCTX.debug)
  state = __init_state(aCTX, None)
  state['status'] = 'active'
 return ret

#
#
def stop(aCTX, aArgs):
 """ Function provides stop behavior

 Args:

 Output:
  - status
 """
 ret = {}
 state = aCTX.cache.get('sun2000',{})
 if state.get('status') != 'active':
  ret['status'] = 'NOT_OK'
  ret['info'] = 'inactive'
 else:
  state['status'] = 'inactive'
  aCTX.cache['sun2000'] = state
  ret['status'] = 'OK'
 return ret

#
#
def close(aCTX, aArgs):
 """ Function provides closing behavior, wrapping up data and file handlers before closing

 Args:

 Output:
  - status
 """
 try:
  state['loop'].run_until_complete(con.stop())
 except Exception as e:
  return {'status':'NOT_OK','info':str(e)}
 else:
  return {'status':'OK'}
