"""Module docstring.

REST interface module

"""
__author__= "Zacharias El Banna"                     
__version__ = "17.6.2GA"
__status__= "Production"

import sdcp.PackageContainer as PC

#
# Make proper REST responses 
#
# - encoded as apicall=package.path:module_function
# - module file is prefixed with rest_ , use _ for function names but not module name (!)
# - reads body to find input data
# - returns json:ed response from function
# 
def server():
 from os import getenv, environ
 from sys import stdout, stdin
 from json import loads, dumps
 apicall = getenv("HTTP_X_Z_APICALL")
 PC.log_msg("API: {}".format(apicall))
 (path,void,mod_fun) = apicall.partition(':')
 (module,void,func)  = mod_fun.partition('_')
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
 print "X-Z-API:{}\r".format(module)
 print "X-Z-Func:{}\r".format(func)
 print "X-Z-Path:{}\r".format(path)
 print "Content-Type: application/json\r"
 stdout.flush()
 print ""
 print data

#
# Make proper REST call with arg = body
# - aURL = REST API link - complete
# - aAPI= python-path-to-module (e.g. package.path:module_fun*)
# - aArgs = body/content 
#
#  returns un-json:ed data
def call(aURL, aAPI, aArgs):
 from json import loads, dumps
 from urllib2 import urlopen, Request, HTTPError
 head = { 'Content-Type': 'application/json', 'X-Z-APICALL':aAPI }
 try:
  req = Request(aURL, headers=head, data=dumps(aArgs))
  sock = urlopen(req)
  try: data = sock.read()
  except: data = '{ "rest_response":"no_data" }'
  sock.close()
 except HTTPError, h:
  try: body = loads(h.read())
  except: body = None
  data = { 'rest_response':'httperror', 'body':body, 'info':dict(h.info()), 'code': h.code }
 except Exception, e:
  data = { 'rest_response':'error', 'error':str(e) }
 return loads(data)
