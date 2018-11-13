"""AWX Controller"""
__author__  = "Zacharias El Banna"
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
  from rims.core.common import rest_call
  from rims.core.genlib import basic_auth
  self._token = basic_auth(aAuth['username'],aAuth['password'])['Authorization']
  try:
   if aAuth.get('mode','full') == 'full':
    ret = rest_call("%s/me"%self._node, aHeader = {'Authorization':self._token})
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
 def call(self, query, **kwargs):
  return self.href("%s/%s"%(self._node,query), **kwargs)

 def href(self,aURL, **kwargs):
  from rims.core.common import rest_call
  try:    kwargs['aHeader'].update({'Authorization':self._token})
  except: kwargs['aHeader'] = {'Authorization':self._token}
  return rest_call(aURL, **kwargs)

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
