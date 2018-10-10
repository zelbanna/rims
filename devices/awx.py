"""Module docstring.

AWX API

"""
__author__  = "Zacharias El Banna"
__version__ = "5.2GA"
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
  self._node = aREST

 def __str__(self):
  return "AWX(%s,%s)".format(self._node, self._token)

 #
 # { 'username','password','mode' }
 # mode: 'basic'/'full' auth process
 #
 def auth(self, aAuth):
  from ..core.common import rest_call
  from ..core.genlib import basic_auth
  self._token = basic_auth(aAuth['username'],aAuth['password'])['Authorization']
  try:
   if aAuth.get('mode','full') == 'full':
    ret = rest_call("%s/me"%self._node,None,None,{'Authorization':self._token})
    ret.pop('data',None)
    ret.pop('node',None)
   else:
    ret = {}
  except Exception as e:
   ret['error'] = e[0]
   ret['auth'] = 'NOT_OK'
  else:
   ret['auth'] = 'OK'
  return ret

 def get_token(self):
  return self._token

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
  from ..core.common import rest_call
  head = {'Authorization':self._token}
  try: head.update(aHeader)
  except: pass
  try: res = rest_call(aURL, aArgs, aMethod, head)
  except Exception as e: res = str(e)
  return res

 def fetch_list(self,aBase,aSet):
  ret  = []
  next = aBase
  while True:
   data = self.call(next)['data']
   for row in data['results']:
    ret.append({k:row.get(k) for k in aSet})
   try:
    _,_,page = data['next'].rpartition('?')
    next = "%s?%s"%(base,page)
   except: break
  return ret

 def fetch_dict(self,aBase,aSet,aKey):
  ret  = {}
  next = aBase
  while True:
   data = self.call(next)['data']
   for row in data['results']:
    ret[row[aKey]] ={k:row.get(k) for k in aSet if row.get(aKey) and row[aKey] != ""}
   try:
    _,_,page = data['next'].rpartition('?')
    next = "%s?%s"%(base,page)
   except: break
  return ret
