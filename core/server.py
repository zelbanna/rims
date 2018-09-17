#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Program docstring.

ZDCP Server.

"""
__author__ = "Zacharias El Banna"
__version__ = "4.0GA"
__status__ = "Production"

from os import walk, path as ospath
from json import loads, dumps
from importlib import import_module
from time import localtime, strftime, sleep
from threading import Thread
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from httplib import responses as http_codes
from urllib2 import urlopen, Request, URLError, HTTPError, unquote
from urlparse import parse_qs
from common import Stream


############################### ZDCP Server ############################
#
# Threads
#
class ApiThread(Thread):
 def __init__(self, aID, aVars):
  Thread.__init__(self)  
  self._vars = dict(aVars)
  self.name   = aID
  self.daemon = True
  self.start()

 def __str__(self):
  return "ApiThread(%s):%s"%(self.name,self._vars)

 def run(self):
  httpd = HTTPServer(self._vars['address'], SessionHandler, False)
  httpd._vars = self._vars
  httpd._thread_id  = self.name
  # Prevent the HTTP server from re-binding every handler.
  # https://stackoverflow.com/questions/46210672/
  httpd.socket = self._vars['socket']
  httpd.server_bind = self.server_close = lambda self: None
  try: httpd.serve_forever()
  except: pass

############################ Call Handler ###########################
#
class SessionHandler(BaseHTTPRequestHandler):

 def __init__(self, *args, **kwargs):
  BaseHTTPRequestHandler.__init__(self,*args, **kwargs)
  self.timeout  = 60

 def log_api(self,aAPI,aArgs,aExtra):
  try:
   with open(self.server._vars['settings']['logs']['rest'], 'a') as f:
    f.write(unicode("%s: %s '%s' @ %s (%s)\n"%(strftime('%Y-%m-%d %H:%M:%S', localtime()), aAPI, aArgs, self.server._vars['node'], aExtra.strip())))
  except: pass


 def do_HEAD(self):
  self.send_response(200)
  self.send_header("Content-type", "text/html")
  self.end_headers()

 def do_GET(self):
  self.route()

 def do_POST(self):
  self.route()

 def route(self):
  """ Route request to the right function """
  path,_,query = (self.path.lstrip('/')).partition('/')
  body, headers = 'null',{'X-Thread':self.server._thread_id,'X-Method':self.command,'X-Version':__version__,'Server':'ZDCP','Date':self.date_time_string()}
  if path == 'site':
   api,_,get = query.partition('?')
   (mod,_,fun)    = api.partition('_')
   stream = Stream(self,get)
   headers.update({'Content-Type':'text/html; charset=utf-8','X-Code':200})
   # if True:
   try:
    module = import_module("zdcp.site." + mod)
    getattr(module,fun,None)(stream)
   # else:
   except Exception as e:
    stream.wr("<DETAILS CLASS='web'><SUMMARY CLASS='red'>ERROR</SUMMARY>API:&nbsp; zdcp.site.%s_%s<BR>"%(mod,fun))
    try:
     stream.wr("Type: %s<BR>Code: %s<BR><DETAILS open='open'><SUMMARY>Info</SUMMARY>"%(e[0]['exception'],e[0]['code']))
     try:
      for key,value in e[0]['info'].iteritems():
       stream.wr("%s: %s<BR>"%(key,value))
     except: stream.wr(e[0]['info'])
     stream.wr("</DETAILS>")
    except:
     stream.wr("Type: %s<BR><DETAILS open='open'><SUMMARY>Info</SUMMARY><CODE>%s</CODE></DETAILS>"%(type(e).__name__,str(e)))
    stream.wr("<DETAILS><SUMMARY>Cookie</SUMMARY><CODE>%s</CODE></DETAILS>"%(stream._cookies))
    stream.wr("<DETAILS><SUMMARY>Args</SUMMARY><CODE>%s</CODE></DETAILS></DETAILS>"%(",".join(stream._form.keys())))
   body = stream.output()

  elif path == 'api':
   # REST API  CALL
   extras = {}
   (api,_,get) = query.partition('&')
   (mod,_,fun) = api.partition('_')
   if get:
    for part in get.split("&"):
     (k,_,v) = part.partition('=')
     extras[k] = v
   headers.update({'X-Module':mod, 'X-Function': fun,'Content-Type':"application/json; charset=utf-8",'Access-Control-Allow-Origin':"*"})
   headers['X-Node'] = extras.get('node',self.server._vars['node'] if not mod == 'system' else 'master')
   try:
    try:
     length = int(self.headers.getheader('content-length'))
     args = loads(self.rfile.read(length)) if length > 0 else {}
    except: args = {}
    self.log_api(api,dumps(args),get)
    if headers['X-Node'] == self.server._vars['node']:
     module = import_module("zdcp.rest.%s"%mod)
     module.__add_globals__({'ospath':ospath,'loads':loads,'dumps':dumps,'import_module':import_module,'SC':self.server._vars['settings'],'workers':self.server._vars['workers']})
     body = dumps(getattr(module,fun,None)(args))
    else:
     req  = Request("%s/api/%s"%(self.server._vars['settings']['nodes'][headers['X-Node']],query), headers = { 'Content-Type': 'application/json','Accept':'application/json' }, data = dumps(args))
     try: sock = urlopen(req, timeout = 300)
     except HTTPError as h:
      raw = h.read()
      try:    data = loads(raw)
      except: data = raw
      headers.update({ 'X-Exception':'HTTPError', 'X-Code':h.code, 'X-Info':dumps(dict(h.info())), 'X-Data':data })
     except URLError  as e: headers.update({ 'X-Exception':'URLError', 'X-Code':590, 'X-Info':str(e)})
     except Exception as e: headers.update({ 'X-Exception':type(e).__name__, 'X-Code':591, 'X-Info':str(e)})
     else:
      try: body = sock.read()
      except: pass
      sock.close()
   except Exception as e:
    headers.update({'X-Args':args,'X-Info':str(e),'X-Exception':type(e).__name__,'X-Code':500})

  elif path == 'infra' or path == 'images' or path == 'files':
   query = unquote(query)
   # Infra call
   if query.endswith(".js"):
    headers['Content-type']='application/javascript; charset=utf-8'
   elif query.endswith(".css"):
    headers['Content-type']='text/css; charset=utf-8'
   try:
    if path == 'files':
     param,_,file = query.partition('/')
     fullpath = ospath.join(self.server._vars['settings']['files'][param],file)
    else:
     fullpath = ospath.join(self.server._vars['path'],path,query)
    if fullpath.endswith("/"):
     headers['Content-type']='text/html; charset=utf-8'
     _, _, filelist = next(walk(fullpath), (None, None, []))
     body = "<BR>".join(["<A HREF='{0}'>{0}</A>".format(file) for file in filelist])
    else:
     with open(fullpath, 'rb') as file:
      body = file.read()
   except Exception as e:
    headers.update({'X-Exception':str(e),'X-Query':query,'X-Path':path,'Content-type':'text/html; charset=utf-8','X-Code':404})

  elif path == 'auth':
   headers['Content-type']='application/json; charset=utf-8'
   try:
    length = int(self.headers.getheader('content-length'))
    args = loads(self.rfile.read(length)) if length > 0 else {}
   except: args = {}
   if   query == 'login':
    # Replace with module load and provide correct headers from system_login
    try: tmp = int(args['id'])
    except:
     body = '"NOT_OK"'
    else:
     body = '"OK"'
     from zdcp.core.genlib import random_string
     from datetime import datetime,timedelta
     headers['X-Auth-Token']  = random_string(16)
     headers['X-Auth-Expire'] = (datetime.utcnow() + timedelta(days=30)).strftime("%a, %d %b %Y %H:%M:%S GMT")
  else:
   # Unknown call
   headers.update({'Location':'site/system_login?application=%s'%self.server._vars['settings']['system'].get('application','system'),'X-Code':301})

  code = headers.pop('X-Code',200)
  self.wfile.write("HTTP/1.1 %s %s\r\n"%(code,http_codes[code]))
  headers.update({'Content-Length':len(body),'Connection':'close'})
  for k,v in headers.iteritems():
   self.send_header(k,v)
  self.end_headers()
  self.wfile.write(body)


############################################ MAIN ######################################
from sys import path as syspath
basepath = ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..'))
syspath.insert(1, basepath)

if __name__ == '__main__':
 #
 from zdcp.Settings import SC
 from zdcp.core.common import DB
 from zdcp.rest.system import task_worker
 import socket
 threadcount = 5
 port = int(SC['system']['port'])
 addr = ('', port)
 sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
 sock.bind(addr)
 sock.listen(5)

 args = {'node':SC['system']['id'],'socket':sock,'address':addr,'settings':SC,'workers':{},'path':ospath.join(basepath,'zdcp')}
 api_threads = [ApiThread(n,args) for n in range(threadcount)]
 #
 # Boot up worker threads as well, add necessary global first
 #
 # with DB() as db:
 # count = db.do("SELECT * FROM system_tasks")
 # args['workers']
 # 
 while len(api_threads) > 0:
  # Check if threads are still alive...
  api_threads = [a for a in api_threads if a.is_alive()]
  sleep(10)
 sock.close()
 print "ZDCP shutdown - no active threads(!)"

