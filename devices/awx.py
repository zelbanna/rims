"""Module docstring.

AWX API

"""
__author__  = "Zacharias El Banna"
__version__ = "18.05.31GA"
__status__  = "Production"
__type__    = "controller"

######################################### AWX REST API ######################################
#
# AWX Class
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
  return "AWX[{}] Token[{},{}]".format(self._node, self._token, self._expire)

 #
 # { 'username','password' }
 #
 def auth(self, aAuth):
  from sdcp.core.common import rest_call,basic_auth
  token = basic_auth(aAuth['username'],aAuth['password'])['Authorization']
  try:
   ret = rest_call("%s/me"%self._node,None,None,{'Authorization':token})
   ret.pop('data',None)
   ret.pop('node',None)
  except Exception as e:
   ret = e[0]
   ret['auth'] = 'NOT_OK'
  else:
   self._token = token
   ret['auth'] = 'OK'
  print dumps(ret,indent=4)
  return ret

 def get_token(self):
  return self._token

 def get_cookie_expire(self):
  return None

 def get_token_expire(self):
  return None

 # call and href
 # Input:
 # - url  = service url
 # - args = dict with arguments for post operation, empty dict or nothing means no arguments (!)
 # - method = used to send other things than GET and POST (i.e. 'DELETE')
 # - header = send additional headers as dictionary
 #
 def call(self,query,args = None, method = None, header = None):
  return self.href("%s/%s"%(self._node,query), aArgs=args, aMethod=method, aHeader = header)

 def href(self,aURL, aArgs = None, aMethod = None, aHeader = None):
  from sdcp.core.common import rest_call
  head = {'Authorization':self._token}
  try: head.update(aHeader)
  except: pass
  try: res = rest_call(aURL, aArgs, aMethod, head)
  except Exception as e: res = e[0]
  return res
