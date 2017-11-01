"""Module docstring.

REST interface module

"""
__author__= "Zacharias El Banna"                     
__version__ = "17.10.4"
__status__= "Production"

# import sdcp.PackageContainer as PC

#
# Make proper REST responses 
#
# - encoded as apicall=package.path.module_function (module cannot contain '_', but function can)
# - reads body to find input data
# - returns json:ed response from function
# -- Response model
# --- res: OK/NOT_OK, ERROR, NO_DATA
# --- type: of ERROR
# --- exception: type of Exception
# --- info: data from api or ERROR info
# --- anything-else: up to developer
#

def server():
 from os import getenv, environ
 from sys import stdout, stdin
 from json import loads, dumps
 api = getenv("HTTP_X_Z_APICALL")
 try:
  if api:
   body = stdin.read()
   args = loads(body if len(body) > 0 else '{"args":"empty"}')
  else:
   try:
    args = dict(map(lambda x: x.split('='),getenv("QUERY_STRING").split("&")))
   except:
    raise  Exception('No Module/Function found for REST API (Query String)')
   api  = args.pop('call')
  (mod,void,fun) = api.partition('_')
  from importlib import import_module
  module = import_module(mod)
  data   = dumps(getattr(module,fun,lambda x: { 'res':'ERROR', 'type':'REST_SERVER_FUNCTION', 'api':api, 'info':'No such function in module', 'args':x })(args))
  print "X-Z-Res:{}\r".format("OK")
  print "X-Z-Mod:{}\r".format(mod)
  print "X-Z-Fun:{}\r".format(fun)
 except Exception, e:
  print "X-Z-Res:{}\r".format(str(e))
  data = dumps({ 'res':'ERROR', 'type':'REST_SERVER', 'exception':type(e).__name, 'api':api, 'info':str(e), 'args':args  }, sort_keys=True)
 print "Content-Type: application/json\r"
 stdout.flush()
 print ""
 print data

#
# Make proper REST call with arg = body
# - aURL = REST API link - complete
# - aAPI= python-path-to-module (e.g. package.path:module_fun*)
# - aArgs = body/content if available
#
#  returns un-json:ed data
def call(aURL, aAPI, aArgs = None):
 from json import loads, dumps
 from urllib2 import urlopen, Request, HTTPError
 head = { 'Content-Type': 'application/json', 'X-Z-APICALL':aAPI }
 try:
  req = Request(aURL, headers=head, data=dumps(aArgs) if aArgs else None)
  sock = urlopen(req)
  try: data = loads(sock.read())
  except: data = { 'res':'NO_DATA' }
  sock.close()
 except HTTPError, h:
  try: body = loads(h.read())
  except: body = None
  data = { 'res':'ERROR', 'type':'REST_CALL_HTTP', 'exception':'HTTPError', 'body':body, 'info':dict(h.info()), 'code': h.code }
 except Exception, e:
  data = { 'res':'ERROR', 'type':'REST_CALL', 'exception':type(e).__name__, 'info':str(e) }
 if data['res'] == 'ERROR':
  raise Exception(data)
 else:
  return data
