"""Module docstring.

AWX API

"""
__author__  = "Zacharias El Banna"
__version__ = "1.0GA"
__status__  = "Production"
__type__    = "controller"

######################################### AWX REST API ######################################
#
# AWX Class
#
class Device(object):

 @classmethod
 def get_functions(cls):
  return ['manage']

 def __init__(self, aREST, aToken = None):
  self._token = aToken
  self._expire = None
  self._node = aREST

 def __str__(self):
  return "AWX[{}] Token[{},{}]".format(self._node, self._token, self._expire)

 #
 # { 'username','password','mode' }
 # mode: 'basic'/'full' auth process
 #
 def auth(self, aAuth):
  from zdcp.core.common import rest_call,basic_auth
  self._token = basic_auth(aAuth['username'],aAuth['password'])['Authorization']
  try:
   if aAuth.get('mode','full') == 'full':
    ret = rest_call("%s/me"%self._node,None,None,{'Authorization':self._token})
    ret.pop('data',None)
    ret.pop('node',None)
   else:
    ret = {}
  except Exception as e:
   ret = e[0]
   ret['auth'] = 'NOT_OK'
  else:
   ret['auth'] = 'OK'
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
  from zdcp.core.common import rest_call
  head = {'Authorization':self._token}
  try: head.update(aHeader)
  except: pass
  try: res = rest_call(aURL, aArgs, aMethod, head)
  except Exception as e: res = e[0]
  return res

 ##################################### Functions ######################################

 def inventories(self):
  res  = []
  next = "%s/inventories"%self._node
  while next:
   data = self.href(next)['data']
   for row in data['results']:
    res.append({k: row.get(k) for k in ('id','name','url')})
   next = data['next']
  return res

 def hosts(self):
  res  = []
  next = "%s/hosts"%self._node
  while next:
   data = self.href(next)['data']
   for row in data['results']:
    res.append({k:row.get(k) for k in ('id','name','url','inventory','description','enabled','instance_id')})
   next = data['next']
  return res
