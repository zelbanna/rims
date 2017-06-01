"""Module docstring.

REST interface module

"""
__author__= "Zacharias El Banna"                     
__version__ = "1.0GA"
__status__= "Production"

# from sdcp.core.GenLib import log_msg
#
# Make proper REST responses 
#
# - uses GET semantics to find module - encoded as api=module_function
# - reads body to find input data
# - returns json:ed response from function
# 
def rest_server():
 from os import getenv
 from sys import stdout, stdin
 from json import loads, dumps
 from importlib import import_module
 print "Content-Type: application/json\r\n"
 stdout.flush()
 # Assume (!) api = abc_xyz
 api = getenv("QUERY_STRING").partition("=")[2]
 body = stdin.read()
 args = body if len(body) > 0 else '{"args":"empty"}'
 try:
  (module,void,func) = api.partition('_')
  mod = import_module("sdcp.site.rest_" + module)
  fun = getattr(mod,func,lambda x: { 'err':"No such function in module", 'args':x, 'rest_module':module, 'function':func })
  print dumps(fun(loads(args)))
 except Exception as err:
  print dumps({ 'err':'module_error', 'res':str(err), 'rest_module':module, 'function':func }, sort_keys=True)

#
# Make proper REST call with arg = body
# - aurl = base link
# - amod = module
# - args = body/content 
#
#  returns un-json:ed data
def rest_call(aurl,amod,args):
 from json import loads, dumps
 from urllib2 import urlopen, Request, HTTPError
 head = { 'Content-Type': 'application/json' }
 try:
  arg = dumps(args)
  req = Request(aurl + "rest.cgi?api=" + amod, headers=head, data=arg)
  sock = urlopen(req)
  try: data = sock.read()
  except: data = '{ "rest_response":"no_data" }'
  sock.close()
 except HTTPError, h:
  try: body = loads(h.read())
  except: body = None
  data = { 'rest_response':'httperror', 'body':body, 'info':str(h.info()), 'code': h.code }
 except Exception, e:
  data = { 'rest_response':'error', 'error':str(e) }
 return loads(data)
