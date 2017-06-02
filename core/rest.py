"""Module docstring.

REST interface module

"""
__author__= "Zacharias El Banna"                     
__version__ = "17.6.2GA"
__status__= "Production"

from sdcp.core.GenLib import log_msg
#
# Make proper REST responses 
#
# - uses GET semantics to find module - encoded as api=module_function
# - reads body to find input data
# - returns json:ed response from function
# 
def server():
 from os import getenv, environ
 from sys import stdout, stdin
 from json import loads, dumps
 api  = getenv("HTTP_X_Z_API")
 path = getenv("HTTP_X_Z_PATH") if api else "sdcp.site"
 if not api:
  api = getenv("QUERY_STRING").partition("=")[2]
 (module,void,func) = api.partition('_')
 body = stdin.read()
 args = body if len(body) > 0 else '{"args":"empty"}'
 try:
  from importlib import import_module
  mod = import_module(path + ".rest_" + module)
  fun = getattr(mod,func,lambda x: { 'err':"No such function in module", 'args':x })
  data = dumps(fun(loads(args)))
  print "X-Z-Res:{}\r".format("OK")
 except Exception as err:
  print "X-Z-Res:{}\r".format(str(err))
  data = dumps({ 'err':'module_error', 'res':str(err)  }, sort_keys=True)
 print "X-Z-Mod:{}\r".format(module)
 print "X-Z-Func:{}\r".format(func)
 print "X-Z-Path:{}\r".format(path)
 print "Content-Type: application/json\r"
 stdout.flush()
 print ""
 print data

#
# Make proper REST call with arg = body
# - aurl = REST API link - complete
# - amod = module
# - args = body/content 
# - apath= python-path-to-module-named-rest_ (e.g. sdcp.site [.rest_xyz])
#
#  returns un-json:ed data
def call(aurl,amod,args,apath = "sdcp.site"):
 from json import loads, dumps
 from urllib2 import urlopen, Request, HTTPError
 head = { 'Content-Type': 'application/json', 'X-Z-Path':apath, 'X-Z-API':amod }
 try:
  arg = dumps(args)
  req = Request(aurl, headers=head, data=arg)
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
