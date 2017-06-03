"""Module docstring.

Appformix Library

"""
__author__ = "Zacharias El Banna"
__version__ = "17.6.1GA"
__status__ = "Production"

############################################ AppformixRPC ######################################
#
# AppformixRPC Class
#
class AppformixRPC(object):

 def __init__(self, aIP, aToken = None):
  self._token = aToken
  self._token_expire = None
  self._ip = aIP

 def __str__(self):
  return "Controller[{}] Token[{},{}]".format(self._ip, self._token, self._token_expire)

 def dump(self,aFile):
  from json import dump
  with open(aFile,'w') as f:
   dump({'token':self._token, 'token_expire':self._token_expire, 'ip':self._ip },f, sort_keys=True, indent=4)

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
  except:
   pass
  return self._token

 #
 # Basic POST  authentication
 # { 'username','password' }
 #
 def auth(self, aAuth):
  from json import dumps,loads
  from urllib2 import urlopen, Request, URLError, HTTPError
  from time import mktime, strptime
  try:
   head = { 'Content-Type': 'application/json' }
   args = dumps({'UserName': aAuth.get('username'), 'Password': aAuth.get('password') })
   sock = urlopen(Request("http://{}:7000/appformix/controller/v2.0/{}".format(self._ip,"auth_credentials"), headers=head, data=args))
   # If sock code is ok (200) - we can expect to find a token
   if sock.code == 200:
    data = loads(sock.read())
    token = data['Token']
    self._token = token['tokenId']
    self._token_expire = int(mktime(strptime(token['expiresAt'],"%Y-%m-%dT%H:%M:%S.%fZ")))
   sock.close()
   return self._token
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

 def get_auth_token(self):
  return self._token

 #
 # Input:
 # - lnk  = service link
 # - arg  = dict with arguments for post operation, empty dict or nothing means no arguments (!)
 # - method = used to send other things than GET and POST (i.e. 'DELETE')
 #
 def call(self,lnk,arg = {}, method = None):
  from json import loads, dumps
  from urllib2 import urlopen, Request, URLError, HTTPError
  try:
   head = { 'Content-Type': 'application/json', 'X-Auth-Token':self._token }
   if len(arg) == 0:
    req  = Request("http://{}:7000/appformix/controller/v2.0/{}".format(self._ip,lnk), headers=head)
   else:
    args = dumps(arg)
    req  = Request("http://{}:7000/appformix/controller/v2.0/{}".format(self._ip,lnk), headers=head, data=args)
   if method:
    req.get_method = lambda: method
   sock = urlopen(req)
   type,info,code = "OK", sock.info(), sock.code
   try: data = loads(sock.read())
   except: data = None
   sock.close()
  except HTTPError, h:
   type,info,code = "HTTPError",h.info(),h.code
   try: data = loads(h.read())
   except: data = None
  except URLError, u:
   type,info,data,code = "URLError",u,None,None
  except Exception, e:
   type,info,data,code = "Error",e,None,None
  return { 'header':info, 'type':type, 'data':data, 'code':code }
