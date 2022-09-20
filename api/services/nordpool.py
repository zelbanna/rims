"""Nordpool market data module. Implements logics to fetch nordpool price and volume data. Always run daily as prices are fixed the day before  """
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "TELEMETRY"

#
#
def process(aCTX, aArgs):
 """Function checks nordpool API, process data and queue reporting to influxDB bucket

 Args:
  - isodate (optional). ISO format "YYYY-MM-DD"

 Output:
  - status
 """
 ret = {'status':'OK','function':'nordpool_process'}

 state = aCTX.cache.get('nordpool',{'running':aCTX.debug})
 if state['running'] or aArgs.get('isodate'):
  config = aCTX.config['services']['nordpool']
  res = sync(aCTX,{'isodate':aArgs.get('isodate')})
  if res['status'] == 'OK':
   data = res['data']
   tmpl = '{},origin=nordpool,type=pricing,system_id=nordpool,currency={} price=%s %s'.format(config.get('measurement','nordpool'),config.get('currency','EUR'))
   records = [tmpl%(x['price']/1000.0,x['ts']) for x in data]
   aCTX.influxdb.write(records, config['bucket'])
   if aCTX.debug:
    ret['data'] = records
  else:
   ret = res
 else:
  ret['status'] = 'NOT_OK'
  ret['info'] = 'inactive'
 return ret

########################################################################################
#
#
def status(aCTX, aArgs):
 """Function retrives the forecast 24h market prices

 Args:
  - type (required)

 Output:
  - url
 """
 from datetime import date, timedelta
 ret = {}
 isodate = date.today() + timedelta(days = 1)
 date_string = f'{isodate.day:02d}-{isodate.month:02d}-{isodate.year}'
 config = aCTX.config['services']['nordpool']
 state = aCTX.cache.get("nordpool",{})
 if not state:
  state = aCTX.cache['nordpool'] = {'running':False,'tomorrow':None,'prices':None,'next':None}
 return {'status':'OK','url':f"https://www.nordpoolgroup.com/api/marketdata/page/10/?entityName={config['entity']}&endDate={date_string}&currency={config['currency']}", 'state':state}


#
#
def sync(aCTX, aArgs):
 """ Syncronizes entity market data from nordpool, possible historic values

 Args:
  - id (required). Server id on master node
  - isodate (optional). ISO format "YYYY-MM-DD"

 Output:
  - prices. Object
  - status. (operation result)
 """
 from datetime import datetime, date, timedelta
 ret = {}
 config = aCTX.config['services']['nordpool']
 state = aCTX.cache.get("nordpool",{})
 if not state:
  state = aCTX.cache['nordpool'] = {'running':False,'tomorrow':None,'prices':None,'next':None}

 today = date.today()
 isodate = today + timedelta(days = 1) if not aArgs.get('isodate') else datetime.fromisoformat(aArgs['isodate'])
 date_string = f'{isodate.day:02d}-{isodate.month:02d}-{isodate.year}'
 url = f"https://www.nordpoolgroup.com/api/marketdata/page/10/?entityName={config['entity']}&endDate={date_string}&currency={config['currency']}"

 try:
  prices = aCTX.rest_call(url, aSSL = aCTX.ssl, aMethod = 'GET')
 except Exception as e:
  ret['info'] = str(e)
  ret['status'] = 'NOT_OK'
 else:
  if prices['data']['Rows'][0]['Columns'][0]['Name'] == date_string:
   ret['data'] = records = []
   for i,x in enumerate(prices['data']['Rows'][:24]):
    ts = int(datetime.timestamp(datetime.fromisoformat(x['StartTime'])))
    price = float(x['Columns'][0]['Value'].replace(" ","").replace(",","."))
    records.append({'ts':ts,'price':price})

   today_string =  f'{today.day:02d}-{today.month:02d}-{today.year}'
   # If we are fetching current prices, save them
   if today_string == date_string:
    state['prices'] = ret['data']
   # Or if the saved that is today, move next prices to current prices
   elif state['tomorrow'] == today_string and state['next']:
    state['prices'] = state['next']
   # Populate next prices if we have fetched them (automatically)
   if not aArgs.get('isodate'):
    state['next'] = ret['data']
    state['tomorrow'] = date_string
   ret['date'] = date_string
   ret['today'] = today_string
   ret['exchangerate'] = prices['data']['ExchangeRateOfficial']
   ret['status'] = 'OK'
  else:
   ret['status'] = 'NOT_OK'
   ret['info'] = 'no_updated_prices'
   ret['date'] = date_string
   ret['result'] = prices['data']['Rows'][0]['Columns'][0]['Name']
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
 settings = aCTX.config['services'].get('nordpool',{})
 params = ['measurement','bucket','entity','currency']
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}

#
#
def start(aCTX, aArgs):
 """ Function provides start behavior and schedules readout every 2h (so most of the time it won't do anything), this is a one way startup model without stop

 Args:

 Output:
  - status
 """
 ret = {}
 if aCTX.cache.get('nordpool',{}).get('running'):
  ret['status'] = 'NOT_OK'
  ret['info'] = 'active'
 else:
  ret['status'] = 'OK'
  ret['info'] = 'scheduled_nordpool'
  aCTX.cache['nordpool'] = {'running':True,'tomorrow':None,'prices':None,'next':None}
  aCTX.schedule_api_periodic(process,'nordpool_process', 7200, args = aArgs, output = aCTX.debug)
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
