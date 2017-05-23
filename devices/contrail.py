"""Module docstring.

Contrail Library

"""
__author__ = "Zacharias El Banna"
__version__ = "10.5GA"
__status__ = "Production"

############################################ ContrailRPC ######################################
#
# ContrailRPC Class
#
class ContrailRPC(object):

 def __init__(self, aIP):
  self._token = None
  self._token_expire = None
  self._ip = aIP
  self._project = None
  self._project_id = None
  self._catalog = None

 def __str__(self):
  return "Controller[{}] Token[{},{}] Project[{},{}]".format(self._ip, self._token, self._token_expire, self._project,self._project_id)

 def get_id(self):
  return self._project_id

 def get_auth_token(self):
  return self._token

 def dump(self,aFile):
  from json import dump
  with open(aFile,'w') as f:
   dump({'token':self._token, 'token_expire':self._token_expire, 'project':self._project, 'ip':self._ip,'project_id':self._project_id },f, sort_keys=True, indent=4)

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
     self._project = data['project']
     self._project_id = data['project_id']
  except:
   pass
  return self._token

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
    self._token_expire = int(mktime(strptime(token['expires_at'],"%Y-%m-%dT%H:%M:%S.%fZ")))
    self._project = token['project']['name']
    self._project_id = token['project']['id']
    catalog = {}
    for svc in token['catalog']:
     catalog[svc['name']] = svc
    self._catalog = catalog
   sock.close()
   return self._catalog
  except HTTPError, h:
   if h.reason == 'Unauthorized' and h.code == 401:
    pass
   else:
    print "{}\n{}".format(h,h.info())
  except URLError, u:
   print "URLError: {}".format(u)
  except Exception, e:
   print "Error: {}".format(e)
  return None

 #
 # port = string rep of port
 # op   = '<nested-dirs>'
 # arg  = dict with arguments, empty dict means no arg
 #
 def call(self,port,op,arg = {}):
  from json import loads, dumps
  from urllib2 import urlopen, Request, URLError, HTTPError
  try:
   head = { 'Content-Type': 'application/json', 'X-Auth-Token':self._token }
   if len(arg) == 0:
    req  = Request("http://{}:{}/{}".format(self._ip,port,op), headers=head)
   else:
    args = dumps(arg)
    req  = Request("http://{}:{}/{}".format(self._ip,port,op), headers=head, data=args)
   sock = urlopen(req)
   data = sock.read()
   sock.close()
   return loads(data)
  except HTTPError, h:
   error = "HTTPError: {}\n{}".format(h,h.info())
  except URLError, u:
   error = "URLError: {}".format(u)
  except Exception, e:
   error = "Error: {}".format(e)
  return { 'error':error }
