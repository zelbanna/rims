"""ISC Kea API module."""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "DHCP"

from ipaddress import ip_address
from rims.core.common import basic_auth

#
#
def status(aRT, aArgs):
 """Function docstring for status

 Args:

 Output:
 """
 settings = aRT.config['services']['isckea']
 try:
  res = aRT.rest_call('http://%s'%settings['endpoint'], aMethod = 'POST', aHeader = basic_auth(settings['username'],settings['password']), aArgs = {'command':'status-get','service':['dhcp4','dhcp6']})
  res.extend(aRT.rest_call('http://%s'%settings['endpoint'], aMethod = 'POST', aHeader = basic_auth(settings['username'],settings['password']), aArgs = {'command':'config-get','service':['dhcp4','dhcp6']}))
 except Exception as e:
  ret = {'status':'NOT_OK','info':str(e)}
 else:
  ret = {'status':'OK','data':res}
 return ret

#
#
def sync(aRT, aArgs):
 """Function docstring for sync:  reload the DHCP server to use updated info

 Args:
  - id (required). Server id on master node (to match entries belonging to this instance)

 Output:
 """
 ret = {'status':'NOT_OK'}
 settings = aRT.config['services']['isckea']
 try:
  current = aRT.rest_call('http://%s'%settings['endpoint'], aMethod = 'POST', aHeader = basic_auth(settings['username'],settings['password']), aArgs = {'command':'config-get','service':['dhcp4']})
  entries = aRT.node_function('master','ipam','server_macs')(aArgs = {'server_id':17,'alternatives':True})
 except Exception as e:
  ret['info'] = str(e)
 else:
  if current[0]['result'] != 0:  # we didn't get the config
   ret['info'] = current.get('text','NO_FAILURE_DESCRIPTION')
  else:
   arguments = current[0]['arguments']
   arguments.pop('hash',None)
   subnets = {}
   for entry in entries['data']:
    try:
     sub = subnets[entry['network']]
    except:
     sub = subnets[entry['network']] = []
    sub.append({'hw-address':entry['mac'],'hostname':entry['hostname'],'ip-address':entry['ip']})
   for sub in arguments['Dhcp4']['subnet4']:
    try:
     sub['reservations'] = subnets[sub['id']]
    except:
     pass
   try:
    res = aRT.rest_call('http://%s'%settings['endpoint'], aMethod = 'POST', aHeader = basic_auth(settings['username'],settings['password']), aArgs = {'command':'config-set','service':['dhcp4'],'arguments':arguments})
   except:
    pass
   else:
    if res[0]['result'] == 0:
     ret['status'] = 'OK'
     res = aRT.rest_call('http://%s'%settings['endpoint'], aMethod = 'POST', aHeader = basic_auth(settings['username'],settings['password']), aArgs = {'command':'config-write','service':['dhcp4']})
    else:
     ret['status'] = 'NOT_OK'
     ret['info'] = res[0]['text']
 return ret

#
#
def update(aRT, aArgs):
 """Function docstring for check: update specific entry

 Args:
  - id (optional)
  - mac (optional required)
  - ip (optional required)
  - network (optional required)

 Output:
 """
 return {'status':'OK','devices':{}}

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
 return {'status':'NO OP'}

#
#
def parameters(aRT, aArgs):
 """ Function provides parameter mapping of anticipated config vs actual

 Args:

 Output:
  - status
  - parameters
 """
 settings = aRT.config['services'].get('isckea',{})
 params = ['endpoint','username','password']
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}

#
#
def start(aRT, aArgs):
 """ Function provides start behavior

 Args:

 Output:
  - status
 """
 return {'status':'NO OP'}

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
