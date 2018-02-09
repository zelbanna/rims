"""Module docstring.

Appformix Library

"""
__author__ = "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__ = "Production"
__type__ = "controller"

############################################ AppformixRPC ######################################
#
# AppformixRPC Class
#
class Device(object):

 def __init__(self, aIP, aToken = None):
  self._token = aToken
  self._token_expire = None
  self._token_utc = None
  self._ip = aIP

 def __str__(self):
  return "Controller[{}] Token[{},{}]".format(self._ip, self._token, self._token_utc)

 def auth(self, aAuth):
  from ..core.rest import call as rest_call
  from time import mktime, strptime
  try:
   auth = {'UserName': aAuth.get('username'), 'Password': aAuth.get('password'), 'AuthType':'openstack' }
   url  = "http://{}:7000/appformix/controller/v2.0/{}".format(self._ip,"auth_credentials")
   res = rest_call(url,'appformix_login',auth)
   # If sock code is ok (200) - we can expect to find a token
   if res['code'] == 200:
    token = res.pop('data',{})['Token']
    self._token = token['tokenId']
    self._token_utc = token['expiresAt']
    self._token_expire = int(mktime(strptime(token['expiresAt'],"%Y-%m-%dT%H:%M:%S.%fZ")))
    res['auth'] = 'OK'
   else:
    res['auth'] = 'NOT_OK'
  except Exception, e:
   res = e[0]
  return res

 def get_token(self):
  return self._token

 def get_token_utc(self):
  return self._token_utc

 #
 # Input:
 # - url  = service link
 # - arg  = dict with arguments for post operation, empty dict or nothing means no arguments (!)
 # - method = used to send other things than GET and POST (i.e. 'DELETE')
 #
 def call(self,url,args = None, method = None, header = None):
  return self.href("http://{}:7000/appformix/controller/v2.0/{}".format(self._ip,url), aArgs=args, aMethod=method, aHeader = header)

 def href(self,aURL, aArgs = None, aMethod = None, aHeader = None):
  from ..core.rest import call as rest_call
  head = { 'X-Auth-Token':self._token, 'X-Auth-Type':'openstack' }
  try: head.update(aHeader)
  except: pass
  return rest_call(aURL, "appformix", aArgs, aMethod, head)
