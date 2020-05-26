"""SRX API module. Implements SRX as authentication server"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "AUTHENTICATION"

from rims.devices.srx import Device

#
#
def status(aCTX, aArgs):
 """Function docstring for auth table status

 Args:

 Output:
  - data
 """
 ret = {}
 settings = aCTX.config['srx']
 try:
  with Device(aCTX,settings.get('device_id',0),settings['ip']) as dev:
   ret = dev.auth_table()
 except Exception as e:
  ret = {'status':'NOT_OK','info':str(e)}
 return ret

#
#
def sync(aCTX, aArgs):
 """ Function checks the auth table and add/remove entries

 Args:
  - id (required). Server id on master node
  - users (optional). List of ip/alias objects instead of local ones

 Output:
 """
 ret = {'added':[],'removed':[]}
 settings = aCTX.config['srx']
 users = [{'ip':v['ip'],'alias':v['alias'],'roles':settings['roles']} for v in (aArgs['users'] if aArgs.get('users') else aCTX.tokens.values())]
 try:
  with Device(aCTX,settings.get('device_id',0),settings['ip']) as dev:
   table = dev.auth_table()['data']
   for entry in table:
    try: users.remove(entry)
    except:
     ret['removed'].append(entry)
   for usr in users:
    try: table.remove(usr)
    except: ret['added'].append(usr)
   for rem in ret['removed']:
    try: dev.auth_delete(rem['alias'],rem['ip'])
    except: pass
   for add in ret['added']:
    try: dev.auth_adde(add['alias'],add['ip'],settings['roles'])
    except: pass
 except Exception as e:
  ret['status'] = 'NOT_OK'
  ret['info'] = str(e)
 else:
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
  - status 'OK'/'NOT_OK'
 """
 return {'status':'OK','code':0,'output':""}

#
#
def authenticate(aCTX, aArgs):
 """ Function adds authentication entry

 Args:
  - alias
  - ip

 Output:
  - status
 """
 settings = aCTX.config['srx']
 try:
  with Device(aCTX,settings.get('device_id',0),settings['ip']) as dev:
   ret = dev.auth_add(aArgs['alias'],aArgs['ip'],settings['roles'])
 except Exception as e:
  ret = {'status':'NOT_OK','info':str(e)}
 return ret

#
#
def invalidate(aCTX, aArgs):
 """ Function removes authentication entry

 Args:
  - alias
  - ip

 Output:
 """
 settings = aCTX.config['srx']
 try:
  with Device(aCTX,settings.get('device_id',0),settings['ip']) as dev:
   ret = dev.auth_delete(aArgs['alias'],aArgs['ip'])
 except Exception as e:
  ret = {'status':'NOT_OK','info':str(e)}
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
 settings = aCTX.config.get('srx',{})
 params = ['device_id','ip','roles']
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}
