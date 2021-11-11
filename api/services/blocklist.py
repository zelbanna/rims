"""BlockList API module. Fetches and prepares a consolidated "internal" list of IP addresses """
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "SECURITY"

#
#
def status(aCTX, aArgs):
 """Function gives time of last consolidation.

 Args:
  - type (required)

 Output:
  - data
 """
 from time import strftime
 sync = aCTX.cache.get('blocklist')
 return {'data':{'time':strftime('%Y-%m-%d %H:%M:%S', sync['time']),'status':sync['status']}, 'status':'OK' } if sync else {'data':{'time':'N/A','status':'NOT_OK'}, 'status':'OK' }

#
#
def sync(aCTX, aArgs):
 """No OP

 Args:
  - id (required). Server id on master node

 Output:
  - code. (error code, optional)
  - output. (output from command)
  - status. (operation result)
 """
 return update(aCTX, aArgs)

#
#
def update(aCTX, aArgs):
 """ Fetch list from

 Args:
  - file

 Output:
  - code. (error code, optional)
  - output. (output from command)
  - status. (operation result)
 """
 from time import localtime
 from urllib import request
 from ipaddress import ip_address

 ret = {'status':'OK','code':'','output':{},'count':0}
 ip_addresses ={}
 for url in aCTX.config['blocklist']['urls']:
  try:
   response = request.urlopen(url)
  except Exception as e:
   ret['output'][url] = e.status
  else:
   for x in response.read().decode().split('\n'):
    try:
     ip_address(x)
    except:
     pass
    else:
     ip_addresses[x] = ip_addresses.get(x,0) + 1
     ret['count'] +=1
   ret['output'][url] = response.status

 blocklistfile = aArgs.get('file',aCTX.config['blocklist'].get('file','site/blocklist.txt'))
 try:
  with open(blocklistfile,'w+') as f:
   for r in ip_addresses.keys():
    f.write(f'{r}\n')
 except Exception as e:
  ret['status'] = 'NOT_OK'
  ret['code'] = str(e)

 aCTX.cache['blocklist'] = {'time':localtime(),'status':ret['status']}

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
 settings = aCTX.config.get('blocklist',{})
 params = ['urls']
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

