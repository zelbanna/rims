"""Module docstring.

Appformix Library

"""
__author__ = "Zacharias El Banna"
__version__ = "18.04.07GA"
__status__ = "Production"
__type__ = "controller"

############################################ AppformixRPC ######################################
#
# AppformixRPC Class
#
class Device(object):

 @classmethod
 def get_functions(cls):
  return []

 def __init__(self, aREST, aToken = None):
  self._token = aToken
  self._expire = None
  self._node = aREST

 def __str__(self):
  return "Controller[{}] Token[{},{}]".format(self._node, self._token, self._expire)

 def auth(self, aAuth):
  from sdcp.core.common import rest_call
  try:
   auth = {'UserName': aAuth.get('username'), 'Password': aAuth.get('password'), 'AuthType':'openstack' }
   url  = "%s:7000/appformix/controller/v2.0/%s"%(self._node,"auth_credentials")
   print url
   res = rest_call(url,auth)
   # If sock code is ok (200) - we can expect to find a token
   if res['code'] == 200:
    token = res.pop('data',{})['Token']
    self._token = token['tokenId']
    self._expire = token['expiresAt']
    res['auth'] = 'OK'
   else:
    res['auth'] = 'NOT_OK'
  except Exception as e:
   res = e[0]
  return res

 def get_token(self):
  return self._token

 def get_cookie_expire(self):
  from datetime import datetime
  return datetime.strptime(self._expire,"%Y-%m-%dT%H:%M:%S.%fZ").strftime("%a, %d %b %Y %H:%M:%S GMT")

 def get_token_expire(self):
  from datetime import datetime,timedelta
  return int((datetime.strptime(self._expire,"%Y-%m-%dT%H:%M:%S.%fZ") - datetime(1970,1,1)).total_seconds())

 #
 # Input:
 # - url  = service link
 # - arg  = dict with arguments for post operation, empty dict or nothing means no arguments (!)
 # - method = used to send other things than GET and POST (i.e. 'DELETE')
 #
 def call(self,url,args = None, method = None, header = None):
  return self.href("%s:7000/appformix/controller/v2.0/%s"%(self._node,url), aArgs=args, aMethod=method, aHeader = header)

 def href(self,aURL, aArgs = None, aMethod = None, aHeader = None):
  from sdcp.core.common import rest_call
  head = { 'X-Auth-Token':self._token, 'X-Auth-Type':'openstack' }
  try: head.update(aHeader)
  except: pass
  return rest_call(aURL,aArgs, aMethod, head)
