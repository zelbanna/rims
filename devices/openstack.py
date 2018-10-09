"""Module docstring.

Openstack Device

"""
__author__  = "Zacharias El Banna"
__version__ = "5.1GA"
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

 def __init__(self, aURL = None, aToken = None):
  self._url   = aURL
  self._token = aToken
  self._expire = None
  self._services = None

 def __str__(self):
  return "Controller[%s,%s,%s]"%(self._url, self._token, self._expire)

 #
 # Keystone v3 authentication - using v2.0 compatible domain (default), project = admin unless specified
 # { 'username','password', 'project' }
 #
 def auth(self, aAuth, aURL = None):
  from ..core.common import rest_call
  try:
   auth = {'auth': {'scope':{'project':{ "name":aAuth.get('project',"admin"), "domain":{'name':'Default'}}},'identity':{'methods':['password'], "password":{"user":{"name":aAuth['username'],"domain":{"name":"Default"},"password":aAuth['password']}}}}}
   url  = "%s/v3/auth/tokens"%(aURL if aURL else self._url)
   res  = rest_call(url,auth)
   # If sock code is created (201), not ok (200) - we can expect to find a token
   if res['code'] == 201:
    token = res.pop('data',{})['token']
    self._token = res['info'].get('x-subject-token')
    self._expire = token['expires_at']
    services = {}
    for svc in token['catalog']:
     services[svc['name']] = svc
    self._services = services
    res['auth'] = 'OK'
   else:
    res['auth'] = 'NOT_OK'
  except Exception as e:
   res = e[0]
   res['auth'] = 'NOT_OK'
  return res

 #
 #
 def projects(self, aURL = None):
  query = self.call("%s/v3/projects"%(aURL if aURL else self._url))
  projects = []
  if query['code'] == 200:
   for project in query['data']['projects']:
    projects.append({'name':project['name'], 'id':project['id']})
  return projects

 def get_token(self):
  return self._token

 def get_services(self):
  return self._services

 def get_cookie_expire(self):
  from datetime import datetime
  return (datetime.strptime(self._expire,"%Y-%m-%dT%H:%M:%S.%fZ")).strftime('%a, %d %b %Y %H:%M:%S GMT')

 def get_token_expire(self):
  from datetime import datetime
  return int((datetime.strptime(self._expire,"%Y-%m-%dT%H:%M:%S.%fZ") - datetime(1970,1,1)).total_seconds())

 def get_service(self,aService,aType):
  ret = {'url':None,'id':None}
  for svc in self._services[aService]['endpoints']:
   if svc['interface'] == aType:
    ret['url'] = svc['url']
    ret['id']   = svc['id']
    break
  return ret

 # Input:
 # - url  = entire service url
 # - query= base url appended with proper query
 # - args = dict with arguments for post operation, empty dict or nothing means no arguments (!)
 # - method = used to send other things than GET and POST (i.e. 'DELETE')
 # - header = send additional headers as dictionary
 #
 def call(self, aURL = None, aArgs = None, aMethod = None, aHeader = None):
  from ..core.common import rest_call
  head = { 'X-Auth-Token':self._token }
  try: head.update(aHeader)
  except: pass
  try: res = rest_call(aURL if aURL else self._url, aArgs, aMethod, head)
  except Exception as e: res = e[0]
  return res
