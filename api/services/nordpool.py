"""Nordpool market data module. Implements logics to fetch nordpool price and volumen data. Always run daily as prices are fixed the day before  """
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "TELEMETRY"

#
#
def process(aCTX, aArgs):
 """Function checks nordpool API, process data and queue reporting to influxDB bucket

 Args:
  - datestring (optional). "DD-MM-YYYY"

 Output:
  - status
 """
 ret = {'status':'OK','function':'nordpool_process'}

 state = aCTX.cache.get('nordpool',{'status':'active' if aCTX.debug else 'inactive'})
 if state['status'] == 'active':
  config = aCTX.config['services']['nordpool']
  res = sync(aCTX,{'datestring':aArgs.get('datestring')})
  if res['status'] == 'OK':
   data = res['data']
   tmpl = '{0},origin=nordpool,type=pricing,system_id=nordpool,year={1},month={2},day={3},hour=%s,currency={4} price=%s %s'.format(config.get('measurement','nordpool'),res['year'],res['month'],res|'day'],config.get('currency','EUR'))
   records = [tmpl%(f"{x['slot']:02d}",x['price'],x['ts']) for x in data]
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

 https://www.nordpoolgroup.com/api/marketdata/page/194?entityName=SE3&endDate=21-06-2022

 Args:
  - type (required)

 Output:
  - url
 """
 from datetime import date, timedelta
 ret = {}
 tomorrow = date.today() + timedelta(days = 1)
 tm_string = f'{tomorrow.day:02d}-{tomorrow.month:02d}-{tomorrow.year}'
 config = aCTX.config['services']['nordpool']
 return {'status':'OK','url':f"https://www.nordpoolgroup.com/api/marketdata/page/10/?entityName={config['entity']}&endDate={tm_string}&currency={config['currency']}"}


#
#
def sync(aCTX, aArgs):
 """ Syncronizes entity market data from nordpool, possible historic values

 Args:
  - id (required). Server id on master node
  - datestring (optional). "DD-MM-YYYY"

 Output:
  - prices. Object
  - status. (operation result)
 """
 from datetime import datetime, date, timedelta
 ret = {}
 tomorrow = date.today() + timedelta(days = 1) if not aArgs.get('datestring') else aArgs['datestring']
 tm_string = f'{tomorrow.day:02d}-{tomorrow.month:02d}-{tomorrow.year}'
 config = aCTX.config['services']['nordpool']
 url = f"https://www.nordpoolgroup.com/api/marketdata/page/10/?entityName={config['entity']}&endDate={tm_string}&currency={config['currency']}"
 try:
  prices = aCTX.rest_call(url, aSSL = aCTX.ssl, aMethod = 'GET')
 except Exception as e:
  ret['info'] = str(e)
  ret['status'] = 'NOT_OK'
 else:
  ret['data'] = records = []
  for i,x in enumerate(prices['data']['Rows'][:24]):
   ts = int(datetime.timestamp(datetime.fromisoformat(x['StartTime'])))
   price = float(x['Columns'][0]['Value'].replace(" ","").replace(",","."))
   records.append({'slot':i, 'ts':ts,'price':price})
  ret['exchangerate'] = prices['data']['ExchangeRateOfficial']
  ret['year'] = tomorrow.year
  ret['month'] = tomorrow.month
  ret['day'] = tomorrow.day
  ret['status'] = 'OK'
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
 """ Function provides start behavior

 Args:

 Output:
  - status
 """
 ret = {'info':'scheduled_nordpool'}
 state = aCTX.cache.get('nordpool',{})
 if state.get('status') == 'active':
  ret['status'] = 'NOT_OK'
  ret['info'] = 'active'
 else:
  ret['status'] = 'OK'
  config = aCTX.config['services']['nordpool']
  aCTX.schedule_api_periodic(process,'nordpool_process', 87600, args = aArgs, output = aCTX.debug)
  aCTX.cache['nordpool'] = {'status':'active'}
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
