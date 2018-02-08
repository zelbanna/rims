"""Module docstring.

REST interface module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"

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
 args,mod,fun = None,None,None
 try:
  if api:
   data = stdin.read()
   args = loads(data if len(data) > 0 else '{}')
  else:
   try:
    args = dict(map(lambda x: x.split('='),getenv("QUERY_STRING").split("&")))
   except:
    raise  Exception('No Module/Function found for REST API (Query String)')
   else:
    api  = args.pop('call')
  (mod,void,fun) = api.partition('_')
  from importlib import import_module
  module = import_module("sdcp.rest.%s"%mod)
  output = dumps(getattr(module,fun,None)(args))
 except Exception, e:
  output = 'null'
  stdout.write("X-Z-Res:ERROR\r\n")
  stdout.write("X-Z-Arguments:%s\r\n"%args)
  stdout.write("X-Z-Info:%s\r\n"%str(e))
  stdout.write("X-Z-Exception:%s\r\n"%type(e).__name__)
 else:
  stdout.write("X-Z-Res:OK\r\n")
 stdout.write("X-Z-Mod:%s\r\n"%mod)
 stdout.write("X-Z-Fun:%s\r\n"%fun)
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
def call(aURL, aAPI, aArgs = None, aMethod = None, aHeader = None, aVerify = None, aTimeout = 20):
 from json import loads, dumps
 from urllib2 import urlopen, Request, URLError, HTTPError
 try:
  head = { 'Content-Type': 'application/json', 'X-Z-APICALL':aAPI }
  try:    head.update(aHeader)
  except: pass
  req = Request(aURL, headers = head, data = dumps(aArgs) if aArgs else None)
  if aMethod:
   req.get_method = lambda: aMethod
  if aVerify is None or aVerify is True:
   sock = urlopen(req, timeout = aTimeout)
  else:
   from ssl import _create_unverified_context
   sock = urlopen(req,context=_create_unverified_context(), timeout = aTimeout)
  output = {'info':dict(sock.info()), 'code':sock.code }
  try:    output['data'] = loads(sock.read())
  except: output['data'] = None
  output['result'] = output['info'].get('x-z-res','OK')
  if output['result'] == 'ERROR':
   output['info'].pop('server',None)
   output['info'].pop('connection',None)
   output['info'].pop('transfer-encoding',None)
  sock.close()
 except HTTPError, h:
  raw = h.read()
  try:    data = loads(raw)
  except: data = raw
  output = { 'result':'ERROR', 'exception':'HTTPError', 'code':h.code, 'info':dict(h.info()), 'data':data }
 except URLError, e:
  output = { 'result':'ERROR', 'exception':'URLError',  'code':590, 'info':str(e)}
 except Exception, e:
  output = { 'result':'ERROR', 'exception':type(e).__name__, 'code':591, 'info':str(e)}
 if output['result'] == "ERROR":
  raise Exception(output)
 return output

#
# Basic Auth header generator
#
def basic_auth(aUsername,aPassword):
 return {'Authorization':'Basic ' + (("%s:%s"%(aUsername,aPassword)).encode('base64')).replace('\n','') }
