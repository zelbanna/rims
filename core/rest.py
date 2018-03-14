"""Module docstring.

REST Server module

"""
__author__= "Zacharias El Banna"
__version__ = "18.03.07GA"
__status__= "Production"

#
# Make proper REST responses
#
# - encoded as apicall=package.path.module_function (module cannot contain '_', but function can)
# - reads body to find input data
# - returns json:ed response from function
# -- Response model
# --- res: OK/NOT_OK, ERROR
# --- type: of ERROR
# --- info: ERROR info
# --- exception: type of Exception
# --- data: data

def server(aNodeID):
 from os import getenv
 from sys import stdout, stdin
 from json import loads, dumps
 from importlib import import_module
 query,output,api,args,mod,fun,additional= getenv("QUERY_STRING"),'null',None,None,None,None,{}
 (api,void,extra) = query.partition('&')
 (mod,void,fun) = api.partition('_')
 try:
  data = stdin.read()
  args = loads(data) if len(data) > 0 else {}
  if extra:
   for part in extra.split("&"):
    (k,void,v) = part.partition('=')
    additional[k] = v
  node = additional.get('node','master')
  if node == aNodeID:
   module = import_module("sdcp.rest.%s"%mod)
   output = dumps(getattr(module,fun,None)(args))
   stdout.write("X-Z-Res:OK\r\n")
  else:
   stdout.write("X-Z-Node:%s\r\n"%node)
   from common import SC,rest_call
   try: res = rest_call("%s?%s"%(SC.node[node],query),args)
   except Exception as err: raise Exception(err)
   else: output = dumps(res['data'])
   stdout.write("X-Z-Res:%s\r\n"%res['info']['x-z-res'])
 except Exception, e:
  stdout.write("X-Z-Res:ERROR\r\n")
  stdout.write("X-Z-Args:%s\r\n"%args)
  stdout.write("X-Z-Info:%s\r\n"%str(e))
  stdout.write("X-Z-Xcpt:%s\r\n"%type(e).__name__)
 stdout.write("X-Z-Mod:%s\r\n"%mod)
 stdout.write("X-Z-Func:%s\r\n"%fun)
 stdout.write("Content-Type: application/json\r\n")
 stdout.flush()
 stdout.write("\r\n")
 stdout.write(output)
