"""Module docstring.

Openstack Library

"""
__author__ = "Zacharias El Banna"
__version__ = "17.6.1GA"
__status__ = "Production"

############################################ OpenstackRPC ######################################
#
# OpenstackRPC Class
#
class OpenstackRPC(object):

 def __init__(self, aIP, aToken = None):
  self._token = aToken
  self._token_expire = None
  self._token_utc = None
  self._ip = aIP
  self._project = None
  self._project_id = None
  self._catalog = None

 def __str__(self):
  return "Controller[{}] Token[{},{}] Project[{},{}]".format(self._ip, self._token, self._token_utc, self._project,self._project_id)

 #
 # Keystone v3 authentication - using v2.0 compatible domain (default), project = admin unless specified
 # { 'username','password', 'project' }
 #
 def auth(self, aAuth):
  from json import dumps,loads
  from urllib2 import urlopen, Request, URLError, HTTPError
  from time import mktime, strptime
  try:
   head = { 'Content-Type': 'application/json' }
   auth = {'auth': {'scope':{'project':{ "name":aAuth.get('project',"admin"), "domain":{'name':'Default'}}},'identity':{'methods':['password'], "password":{"user":{"name":aAuth['username'],"domain":{"name":"Default"},"password":aAuth['password']}}}}}
   args = dumps(auth)
   sock = urlopen(Request("http://{}:{}/{}".format(self._ip,"5000","v3/auth/tokens"), headers=head, data=args))
   # If sock code is created (201), not ok (200) - we can expect to find a token
   if sock.code == 201:
    data = loads(sock.read())
    token = data['token']
    self._token = sock.info().get('x-subject-token')
    self._token_utc = token['expires_at'] 
    self._token_expire = int(mktime(strptime(token['expires_at'],"%Y-%m-%dT%H:%M:%S.%fZ")))
    self._project = token['project']['name']
    self._project_id = token['project']['id']
    catalog = {}
    for svc in token['catalog']:
     catalog[svc['name']] = svc
    self._catalog = catalog
   result, code, info  = "OK", sock.code, None
   sock.close()
  except HTTPError, h:
   result,code,info = h.reason,h.code,str(h)
  except URLError, u:
   result,code,info = "URLError",590,str(u)
  except Exception, e:
   result,code,info = "Error",591,str(e)
  return {'result':result, 'code':code, 'info':info }

 def get_id(self):
  return self._project_id

 def get_token(self):
  return self._token

 def get_catalog(self):
  return self._catalog

 def get_expire_utc(self):
  return self._token_utc
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

 #
 # Input:
 # - port = base port
 # - lnk  = service link
 # - arg  = dict with arguments for post operation, empty dict or nothing means no arguments (!)
 # - method = used to send other things than GET and POST (i.e. 'DELETE')
 #
 def call(self,port,lnk,arg = {}, method = None):
  from json import loads, dumps
  from urllib2 import urlopen, Request, URLError, HTTPError
  try:
   head = { 'Content-Type': 'application/json', 'X-Auth-Token':self._token }
   if len(arg) == 0:
    req  = Request("http://{}:{}/{}".format(self._ip,port,lnk), headers=head)
   else:
    args = dumps(arg)
    req  = Request("http://{}:{}/{}".format(self._ip,port,lnk), headers=head, data=args)
   if method:
    req.get_method = lambda: method
   sock = urlopen(req)
   result,info,code = "OK", sock.info(), sock.code
   try: data = loads(sock.read())
   except: data = None
   sock.close()
  except HTTPError, h:
   result,info,code = "HTTPError",h.info(),h.code
   try: data = loads(h.read())
   except: data = None
  except URLError, u:
   result,info,data,code = "URLError",u,None,None
  except Exception, e:
   result,info,data,code = "Error",e,None,None
  return { 'header':info, 'result':result, 'data':data, 'code':code }

 #################################### File OPs ####################################
 #
 # File operations for debugging
 # 
 def dump(self,aFile):
  from json import dump
  with open(aFile,'w') as f:
   dump({'token':self._token, 'token_utc':self._token_utc, 'token_expire':self._token_expire, 'project':self._project, 'ip':self._ip,'project_id':self._project_id, 'catalog':self._catalog },f, sort_keys=True, indent=4)

 def load(self,aFile):
  from json import load
  from datetime import datetime
  try:
   with open(aFile,'r') as f:
    data = load(f)
    if datetime.fromtimestamp(int(data['token_expire'])) > datetime.utcnow():
     self._ip = data['ip']
     self._token = data['token']
     self._token_expire = data['token_expire']
     self._token_utc = data['token_utc']
     self._project = data['project']
     self._project_id = data['project_id']
     self._catalog = data['catalog']
  except:
   pass
  return self._token
