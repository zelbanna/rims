"""SRX API module. Implements SRX as authentication server"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "AUTHENTICATION"

from rims.core.common import basic_auth
from datetime import datetime
#
# Junos configuration:
#
# set services user-identification authentication-source aruba-clearpass no-user-query
# set system services webapi user USERNAME
# set system services webapi user password PASSWORD
# set system services webapi client RIMS-IP
# set system services webapi http port DEST-IP
#

#
#
def status(aCTX, aArgs):
 """Function docstring for auth table status

 Args:

 Output:
  - data
 """
 return {'status':'OK','data':{}}

#
#
def sync(aCTX, aArgs):
 """ Function checks the auth table and add/remove entries (in this case, only updates...)

 Args:
  - id (required). Server id on master node
  - users (optional). List of ip/alias objects instead of local ones

 Output:
 """
 ret = {'added':[],'removed':[]}
 settings = aCTX.config['srx']
 auth = basic_auth(settings['username'], settings['password'])
 ts = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
 argstr = '<?xml version="1.0" encoding="UTF-8"?><userfw-entries><userfw-entry><source>Aruba ClearPass</source><timestamp>%s</timestamp><operation>logon</operation><timeout>%s</timeout><IP>%s</IP><domain>global</domain><user>%s</user><role-list><role>%s</role></role-list><posture>healthy</posture></userfw-entry></userfw-entries>'
 users = aArgs['users'] if aArgs.get('users') else aCTX.tokens.values()
 try:
  for usr in users:
   print('authenticating: %s'%usr)
   aCTX.rest_call('%s/api/userfw/v1/post-entry'%settings['url'], aHeader = auth, aApplication = 'xml', aArgs = argstr%(ts, 7200, usr['ip'], usr['alias'],"</role><role>".join(settings['roles'])))
   ret['added'] = usr['alias']
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
  - alias (required)
  - ip (required)
  - timeout (optional)

 Output:
  - status
 """
 settings = aCTX.config['srx']
 auth = basic_auth(settings['username'], settings['password'])
 ts = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
 argstr = '<?xml version="1.0" encoding="UTF-8"?><userfw-entries><userfw-entry><source>Aruba ClearPass</source><timestamp>%s</timestamp><operation>logon</operation><timeout>%s</timeout><IP>%s</IP><domain>global</domain><user>%s</user><role-list><role>%s</role></role-list><posture>healthy</posture></userfw-entry></userfw-entries>'
 try: aCTX.rest_call('%s/api/userfw/v1/post-entry'%settings['url'], aHeader = auth, aApplication = 'xml', aArgs = argstr%(ts, aArgs.get('timeout',7200), aArgs['ip'], aArgs['alias'],"</role><role>".join(settings['roles'])))
 except Exception as e:
  ret = {'status':'NOT_OK','info':str(e)}
 else:
  ret = {'status':'OK'}
 return ret

#
#
def invalidate(aCTX, aArgs):
 """ Function removes authentication entry

 Args:
  - alias (required)
  - ip (required)

 Output:
 """
 settings = aCTX.config['srx']
 auth = basic_auth(settings['username'], settings['password'])
 ts = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
 argstr = '<?xml version="1.0" encoding="UTF-8"?><userfw-entries><userfw-entry><source>Aruba ClearPass</source><timestamp>%s</timestamp><operation>logoff</operation><IP>%s</IP></userfw-entry></userfw-entries>'
 try: aCTX.rest_call('%s/api/userfw/v1/post-entry'%settings['url'], aHeader = auth, aApplication = 'xml', aArgs = argstr%(ts, aArgs['ip']))
 except Exception as e:
  ret = {'status':'NOT_OK','info':str(e)}
 else:
  ret = {'status':'OK'}
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
 params = ['url','username','password','roles']
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}
