"""Module docstring.

REST Server module

"""
__author__= "Zacharias El Banna"
__version__ = "1.0GA"
__status__= "Production"

#
# Centralized REST handler (assumes most calls should go to DB node !!) Very important for:
# - supporting REST nodes
# - any node using this module for serving REST requests
#
# Function:
# - expecting query string encoded as apicall=module_function (module cannot contain '_', but function can)
# - reads body to find input data
# - returns json:ed response from function
# -- Response model
# --- res: OK/NOT_OK, ERROR
# --- type: of ERROR
# --- info: ERROR info
# --- exception: type of Exception
# --- data: data
#
def server(aNodeID):
 from os import getenv, path as ospath, environ
 from sys import stdout, stdin, path as syspath
 from json import loads, dumps
 from importlib import import_module
 from zdcp.SettingsContainer import SC
 query,output,api,args,mod,fun,additional= getenv("QUERY_STRING"),'null',None,None,None,None,{}
 (api,_,extra) = query.partition('&')
 (mod,_,fun) = api.partition('_')
 try:
  data = stdin.read()
  args = loads(data) if len(data) > 0 else {}
  if extra:
   for part in extra.split("&"):
    (k,void,v) = part.partition('=')
    additional[k] = v
  # Node is always master for system calls
  node = additional.get('node',aNodeID if not mod == 'system' else 'master')
  stdout.write("X-API-Node:%s\r\n"%node)
  from zdcp.core.logger import rest as log
  log(node,api,dumps(args),extra)
  if node == aNodeID:
   module = import_module("zdcp.rest.%s"%mod)
   module.__add_globals__({'ospath':ospath,'loads':loads,'dumps':dumps,'import_module':import_module,'SC':SC})
   output = dumps(getattr(module,fun,None)(args))
   stdout.write("X-API-Res:OK\r\n")
  else:
   from zdcp.core.common import rest_call
   try: res = rest_call("%s?%s"%(SC['nodes'][node],query),args)
   except Exception as err: raise Exception(err)
   else: output = dumps(res['data'])
   stdout.write("X-API-Res:%s\r\n"%res['info']['x-api-res'])
 except Exception as e:
  stdout.write("X-API-Res:ERROR\r\n")
  stdout.write("X-API-Args:%s\r\n"%args)
  stdout.write("X-API-Info:%s\r\n"%str(e))
  stdout.write("X-API-Xcpt:%s\r\n"%type(e).__name__)
 stdout.write("X-API-Method:%s\r\n"%environ['REQUEST_METHOD'])
 stdout.write("X-API-Function:%s\r\n"%api)
 stdout.write("Content-Type: application/json\r\n")
 stdout.write("Access-Control-Allow-Origin: *\r\n")
 stdout.flush()
 stdout.write("\r\n")
 stdout.write(output)
