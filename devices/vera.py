"""Module docstring.

Vera Library

"""
__author__  = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__  = "Production"
__type__    = "controller"

from generic import Device as GenericDevice

class Device(GenericDevice):

 def __init__(self,aIP,aID=None):
  GenericDevice.__init__(self,aIP,aID)
  self._token = None

 @classmethod
 def get_widgets(cls):
  return ['operated']

 def __str__(self):
  return "Controller[{}]".format(self._ip)
 
 # call and href
 # Input:
 # - port = base port
 # - url  = service url
 # - args = dict with arguments for post operation, empty dict or nothing means no arguments (!)
 # - method = used to send other things than GET and POST (i.e. 'DELETE')
 # - header = send additional headers as dictionary
 # 
 def call(self,port,query,args = None, method = None, header = None):
  return self.href("http://%s:%i/data_request?%s"%(self._ip,port,query), args=args, method=method, header=header)

 # Native href from openstack - simplify formatting
 def href(self,href,args = None, method = None, header = None):
  from json import loads, dumps
  from urllib2 import urlopen, Request, URLError, HTTPError
  try:
   head = { 'Content-Type': 'application/json', 'X-Auth-Token':self._token }
   try:    head.update(header)
   except: pass
   req  = Request(href, headers=head, data = dumps(args) if args else None)
   if method:
    req.get_method = lambda: method
   sock = urlopen(req)
   result,info,code = "OK", dict(sock.info()), sock.code
   try: data = loads(sock.read())
   except: data = None
   sock.close()
  except HTTPError, h:
   result,info,code = "HTTPError",dict(h.info()),h.code
   raw = h.read()
   try:    data = loads(raw)
   except: data = raw
  except URLError, u:
   result,info,data,code = "URLError",u,None,None
  except Exception, e:
   result,info,data,code = "Error",e,None,None
  return { 'header':info, 'result':result, 'data':data, 'code':code }
