"""Program docstring.

ZDCP Engine

"""
__author__ = "Zacharias El Banna"
__version__ = "4.0GA"
__status__ = "Production"

from os import walk, path as ospath
from json import loads, dumps
from importlib import import_module

from time import localtime, strftime
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from httplib import responses as http_codes
from urllib2 import urlopen, Request, URLError, HTTPError, unquote

########################################## Threads ########################################
#
# Threads
#

from threading import Thread, Lock

class WorkerThread(Thread):

 def __init__(self, aArgs, aSettings, aWorkers):
  """

  Args:
   - id of task to execute
   - module (required)
   - func (required)
   - args (required)
   - type (required)
   - frequency (optional required)
   - output (optional) True/False (default)

  Workers:
   - workers dictionary to register oneself upon
   
  """
  Thread.__init__(self)
  if aArgs.get('id'):
   self.name = aArgs['id']
  else:
   from random import randint
   self.name = 'T%s'%randint(0,10000)
  self.lock = Lock()
  self.exit = False
  self.args = aArgs
  self.workers = aWorkers
  self.settings= aSettings
  self.workers[self.name] = self
  self.result = None
  self.daemon   = True
  self.start()

 def __str__(self):
  return "WorkerThread(%s:%s):%s_%s(%s)"%(self.name,self.args.get('periodic'),self.args['module'],self.args['func'],self.args['args'])

 def pause(self, aBlock = True):
  return self.lock.acquire(aBlock)

 def release(self):
  try:    self.lock.release()
  except: return False
  else:   return True

 def stop(self):
  self.exit = True
  return self.name

 def result(self):
  return self.result

 def run(self):
  from zdcp.core.common import log
  try:          
   mod = import_module("zdcp.rest.%s"%self.args['module'])
   mod.__add_globals__({'ospath':ospath,'loads':loads,'dumps':dumps,'import_module':import_module,'SC':self.settings,'workers':self.workers})
   fun = getattr(mod,self.args['func'],lambda x: {'THREAD_NOT_OK'})
  except Exception as e:
   log("WorkerThread(%s) ERROR => %s"%(self.name,str(e)))
  else:
   if not self.args.get('periodic'):
    self.result = fun(self.args['args'])
   else:
    from time import sleep, time
    while not self.exit:
     with self.lock:
      self.result = fun(self.args['args'])
     if self.args.get('output'):
      log("WorkerThread(%s): %s_%s PERIODIC => %s"%(self.name,self.args['module'],self.args['func'],dumps(self.result)))
     sleep(int(self.args.get('frequency',300)))
  self.workers.pop(self.name,None)
  if self.args.get('output'):
   log("WorkerThread(%s): %s_%s COMPLETE => %s"%(self.name,self.args['module'],self.args['func'],dumps(self.result)))
#
#
class ApiThread(Thread):
 def __init__(self, aID, aContext):
  Thread.__init__(self)  
  self._context = aContext
  self.name     = aID
  self.daemon   = True
  self.start()

 def __str__(self):
  return "ApiThread(%s)"%(self.name)

 def run(self):
  httpd = HTTPServer(self._context['address'], SessionHandler, False)
  httpd._context  = self._context
  httpd._node     = self._context['node']
  httpd._settings = self._context['globals']['SC']
  httpd._globals  = self._context['globals']
  httpd.socket    = self._context['socket']
  httpd._t_id     = self.name
  httpd.server_bind = self.server_close = lambda self: None
  try: httpd.serve_forever()
  except: pass

###################################### Call Handler ######################################
#
class SessionHandler(BaseHTTPRequestHandler):

 def __init__(self, *args, **kwargs):
  BaseHTTPRequestHandler.__init__(self,*args, **kwargs)
  self.timeout  = 60

 def log_api(self,aAPI,aArgs,aExtra):
  try:
   with open(self.server._settings['logs']['rest'], 'a') as f:
    f.write(unicode("%s: %s '%s' @ %s (%s)\n"%(strftime('%Y-%m-%d %H:%M:%S', localtime()), aAPI, aArgs, self.server._node, aExtra.strip())))
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
  body, headers = 'null',{'X-Thread':self.server._t_id,'X-Method':self.command,'X-Version':__version__,'Server':'ZDCP','Date':self.date_time_string()}
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
   headers['X-Node'] = extras.get('node',self.server._context['node'] if not mod == 'system' else 'master')
   try:
    try:
     length = int(self.headers.getheader('content-length'))
     args = loads(self.rfile.read(length)) if length > 0 else {}
    except: args = {}
    self.log_api(api,dumps(args),get)
    if headers['X-Node'] == self.server._node:
     module = import_module("zdcp.rest.%s"%mod)
     module.__add_globals__(self.server._globals)
     body = dumps(getattr(module,fun,None)(args))
    else:
     req  = Request("%s/api/%s"%(self.server._settings['nodes'][headers['X-Node']],query), headers = { 'Content-Type': 'application/json','Accept':'application/json' }, data = dumps(args))
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
     fullpath = ospath.join(self.server._settings['files'][param],file)
    else:
     fullpath = ospath.join(self.server._context['path'],path,query)
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
   headers.update({'Location':'site/system_login?application=%s'%self.server._settings['system'].get('application','system'),'X-Code':301})

  code = headers.pop('X-Code',200)
  self.wfile.write("HTTP/1.1 %s %s\r\n"%(code,http_codes[code]))
  headers.update({'Content-Length':len(body),'Connection':'close'})
  for k,v in headers.iteritems():
   self.send_header(k,v)
  self.end_headers()
  self.wfile.write(body)

########################################### Web stream ########################################
#

from urlparse import parse_qs

class Stream(object):

 def __init__(self,aHandler, aGet):
  self._cookies = {}
  self._form    = {}
  self._node    = aHandler.server._node
  self._api     = aHandler.server._settings['system']['node']
  self._body    = []
  try: cookie_str = aHandler.headers.get('Cookie').split('; ')
  except: pass
  else:
   for cookie in cookie_str:
    k,_,v = cookie.partition('=')
    try:    self._cookies[k] = dict(x.split('=') for x in v.split(','))
    except: self._cookies[k] = v
  try:    body_len = int(aHandler.headers.getheader('content-length'))
  except: body_len = 0
  if body_len > 0 or len(aGet) > 0:
   from urlparse import parse_qs
   if body_len > 0:
    self._form.update({ k: l[0] for k,l in parse_qs(aHandler.rfile.read(body_len), keep_blank_values=1).iteritems() })
   if len(aGet) > 0:
    self._form.update({ k: l[0] for k,l in parse_qs(aGet, keep_blank_values=1).iteritems() })

 def __str__(self):
  return "<DETAILS CLASS='web blue'><SUMMARY>Web</SUMMARY>Web object<DETAILS><SUMMARY>Cookies</SUMMARY><CODE>%s</CODE></DETAILS><DETAILS><SUMMARY>Form</SUMMARY><CODE>%s</CODE></DETAILS></DETAILS>"%(str(self._cookies),self._form)

 def output(self):
  return ("".join(self._body)).encode('utf-8')

 def wr(self,aHTML):
  self._body.append(aHTML.decode('utf-8'))

 def node(self):
  return self._node

 def cookie(self,aName):
  return self._cookies.get(aName,{})

 def args(self):
  return self._form

 def __getitem__(self,aKey):
  return self._form.get(aKey,None)

 def get(self,aKey,aDefault = None):
  return self._form.get(aKey,aDefault)

 def get_args2dict(self,aExcept = []):
  return { k:v for k,v in self._form.iteritems() if not k in aExcept }

 def get_args(self,aExcept = []):
  return "&".join(["%s=%s"%(k,v) for k,v in self._form.iteritems() if not k in aExcept])

 def button(self,aImg,**kwargs):
  return " ".join(["<A CLASS='btn z-op small'"," ".join(["%s='%s'"%(key,value) for key,value in kwargs.iteritems()]),"><IMG SRC='../images/btn-%s.png'></A>"%(aImg)])

 # Simplified SDCP REST call
 def rest_call(self, aAPI, aArgs = None, aTimeout = 60):
  from common import rest_call
  return rest_call("%s/api/%s"%(self._api,aAPI), aArgs, aTimeout = 60)['data']

 # Generic REST call with full output
 def rest_full(self, aURL, aArgs = None, aMethod = None, aHeader = None, aTimeout = 20):
  return rest_call(aURL, aArgs, aMethod, aHeader, True, aTimeout)

 def put_html(self, aTitle = None, aIcon = 'zdcp.png'):
  self._body.append("<!DOCTYPE html><HEAD><META CHARSET='UTF-8'><LINK REL='stylesheet' TYPE='text/css' HREF='../infra/4.21.0.vis.min.css' /><LINK REL='stylesheet' TYPE='text/css' HREF='../infra/zdcp.css'>")
  if aTitle:
   self._body.append("<TITLE>" + aTitle + "</TITLE>")
  self._body.append("<LINK REL='shortcut icon' TYPE='image/png' HREF='../images/%s'/>"%(aIcon))
  self._body.append("<SCRIPT SRC='../infra/3.1.1.jquery.min.js'></SCRIPT><SCRIPT SRC='../infra/4.21.0.vis.min.js'></SCRIPT><SCRIPT SRC='../infra/zdcp.js'></SCRIPT>")
  self._body.append("<SCRIPT>$(function() { $(document.body).on('click','.z-op',btn ) .on('focusin focusout','input, select',focus ) .on('input','.slider',slide_monitor); });</SCRIPT>")
  self._body.append("</HEAD>")
