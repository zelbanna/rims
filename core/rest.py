"""Module docstring.

REST interface module

"""
__author__= "Zacharias El Banna"                     
__version__ = "17.11.01GA"
__status__= "Production"

class RestException(Exception):
 '''Raise REST exceptions'''
 def __init__(self,args):
  self._args = args

 def __str__(self):
  return "RestException(%s)"%self._args

 def get(self,aKey = None):
  return self._args if not aKey else self._args.get(aKey,None)

#
# Make proper REST responses
#
# - encoded as apicall=package.path.module_function (module cannot contain '_', but function can)
# - reads body to find input data
# - returns json:ed response from function
# -- Response model
# --- res: OK/NOT_OK, ERROR, NO_DATA
# --- type: of ERROR
# --- info: ERROR info
# --- exception: type of Exception
# --- data: data

def server():
 from os import getenv, environ
 from sys import stdout, stdin
 from json import loads, dumps
 api = getenv("HTTP_X_Z_APICALL")
 try:
  if api:
   data = stdin.read()
   args = loads(data if len(data) > 0 else '{"args":"empty"}')
  else:
   try:
    args = dict(map(lambda x: x.split('='),getenv("QUERY_STRING").split("&")))
   except:
    args = None
    raise  Exception('No Module/Function found for REST API (Query String)')
   api  = args.pop('call')
  (mod,void,fun) = api.partition('_')
  from importlib import import_module
  module = import_module(mod)
  output = dumps(getattr(module,fun,lambda x: { 'result':'ERROR', 'type':'REST_SERVER_FUNCTION', 'api':api, 'exception':'no_such_dunction', 'info':'No such function in module', 'args':x })(args))
  stdout.write("X-Z-Res:OK\r\n")
  stdout.write("X-Z-Mod:{}\r\n".format(mod))
  stdout.write("X-Z-Fun:{}\r\n".format(fun))
 except Exception, e:
  stdout.write("X-Z-Res:ERROR\r\n")
  output= dumps({ 'result':'SERVER_ERROR', 'exception':type(e).__name__, 'api':api, 'info':str(e), 'code':592, 'args':args })
 stdout.write("Content-Type: application/json\r\n")
 stdout.flush()
 stdout.write("\r\n")
 stdout.write(output)

#
# Make proper REST call with arg = data
# - aURL = REST API link - complete
# - aAPI= python-path-to-module (e.g. package.path:module_fun*)
# - aArgs = data/content if available
#
#  returns un-json:ed data
def call(aURL, aAPI, aArgs = None, aMethod = None, aHeader = None):
 from json import loads, dumps
 from urllib2 import urlopen, Request, URLError, HTTPError
 try:
  head = { 'Content-Type': 'application/json', 'X-Z-APICALL':aAPI }
  try:    head.update(aHeader)
  except: pass
  req = Request(aURL, headers = head, data = dumps(aArgs) if aArgs else None)
  if aMethod:
   req.get_method = lambda: aMethod
  sock = urlopen(req)
  output = {'result':'CALL_OK', 'info':dict(sock.info()), 'code':sock.code }
  try:    output['data']   = loads(sock.read())
  except: output['result'] = 'CALL_OK_NO_DATA'
  if output['data'].get('result') == 'SERVER_ERROR':
   output = output['data']
  sock.close()
 except HTTPError, h:
  raw = h.read()
  try:    data = loads(raw)
  except: data = raw
  output = { 'result':'CALL_ERROR', 'exception':'HTTPError',      'info':dict(h.info()), 'code': h.code, 'data':data }
 except URLError, u:
  output = { 'result':'CALL_ERROR', 'exception':'URLError',       'info':str(u), 'code':590 }
 except Exception, e:
  output = { 'result':'CALL_ERROR', 'exception':type(e).__name__, 'info':str(e), 'code':591 }
 if output['result'][-5:] == "ERROR":
  raise RestException(output)  
 return output
