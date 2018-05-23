"""Module docstring.

Openstack Library

"""
__author__  = "Zacharias El Banna"
__version__ = "18.04.07GA"
__status__  = "Production"
__type__    = "controller"

############################################ OpenstackRPC ######################################
#
# OpenstackRPC Class
#
class Device(object):

 @classmethod
 def get_functions(cls):
  return []

 def __init__(self, aREST, aToken = None):
  self._token = aToken
  self._expire = None
  self._node = aREST
  self._project = None
  self._project_id = None
  self._catalog = None

 def __str__(self):
  return "Controller[{}] Token[{},{}] Project[{},{}]".format(self._node, self._token, self._expire, self._project,self._project_id)

 #
 # Keystone v3 authentication - using v2.0 compatible domain (default), project = admin unless specified
 # { 'username','password', 'project' }
 #
 def auth(self, aAuth):
  from sdcp.core.common import rest_call
  try:
   auth = {'auth': {'scope':{'project':{ "name":aAuth.get('project',"admin"), "domain":{'name':'Default'}}},'identity':{'methods':['password'], "password":{"user":{"name":aAuth['username'],"domain":{"name":"Default"},"password":aAuth['password']}}}}}
   url  = "%s:5000/v3/auth/tokens"%(self._node)
   res  = rest_call(url,auth)
   # If sock code is created (201), not ok (200) - we can expect to find a token
   if res['code'] == 201:
    token = res.pop('data',{})['token']
    self._token = res['info'].get('x-subject-token')
    self._expire = token['expires_at']
    self._project = token['project']['name']
    self._project_id = token['project']['id']
    catalog = {}
    for svc in token['catalog']:
     catalog[svc['name']] = svc
    self._catalog = catalog
    res['auth'] = 'OK'
   else:
    res['auth'] = 'NOT_OK'
  except Exception as e:
   res = e[0]
   res['auth'] = 'NOT_OK'
  return res

 def get_id(self):
  return self._project_id

 def get_token(self):
  return self._token

 def get_catalog(self):
  return self._catalog

 def get_cookie_expire(self):
  from datetime import datetime
  return (datetime.strptime(self._expire,"%Y-%m-%dT%H:%M:%S.%fZ")).strftime('%a, %d %b %Y %H:%M:%S GMT')

 def get_token_expire(self):
  from datetime import datetime
  return int((datetime.strptime(self._expire,"%Y-%m-%dT%H:%M:%S.%fZ") - datetime(1970,1,1)).total_seconds())

 #
 # Input: Service, auth-type (admin/internal/public)
 # Returns tuple with:
 # - base port
 # - service link
 # - service id
 def get_service(self,aService,aType):
  for svc in self._catalog[aService]['endpoints']:
   if svc['interface'] == aType:
    # http : //x.y.z : port / lnk
    (port,_,lnk) = svc['url'].split(':')[2].partition('/')
    return (port,lnk,svc['id'])
  else:
   return (None,None,None)

 # call and href
 # Input:
 # - port = base port
 # - url  = service url
 # - args = dict with arguments for post operation, empty dict or nothing means no arguments (!)
 # - method = used to send other things than GET and POST (i.e. 'DELETE')
 # - header = send additional headers as dictionary
 #
 def call(self,port,query,args = None, method = None, header = None):
  return self.href("%s:%s/%s"%(self._node,port,query), aArgs=args, aMethod=method, aHeader = header)

 def href(self,aURL, aArgs = None, aMethod = None, aHeader = None):
  from sdcp.core.common import rest_call
  head = { 'X-Auth-Token':self._token }
  try: head.update(aHeader)
  except: pass
  try: res = rest_call(aURL, aArgs, aMethod, head)
  except Exception as e: res = e[0]
  return res
