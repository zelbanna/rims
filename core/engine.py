"""Program docstring.

ZDCP Engine

"""
__author__ = "Zacharias El Banna"
__version__ = "4.0GA"
__status__ = "Production"

from os import walk, path as ospath
from json import loads, dumps
from importlib import import_module
from threading import Thread, Lock, Event
from time import localtime, strftime, sleep, time
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from httplib import responses as http_codes
from urllib2 import urlopen, Request, URLError, HTTPError, unquote

########################################## Threads ########################################
#
#
class ThreadPool(object):

 def __init__(self, aThreadCount, aSettings):
  from Queue import Queue
  self._queue = Queue(0)
  self._thread_count = aThreadCount
  self._aborts  = []
  self._idles   = [] 
  self._threads = []
  self._settings = aSettings
  self.run()

 def __del__(self):
  self.abort()

 def __str__(self):
  return "ThreadPool(%s)"%(self._thread_count)

 def run(self, aBlock = False):
  if aBlock:
   while self.alive():
    sleep(1)
  elif self.alive():
   return False
  else:
   self._aborts = []
   self._idles = []
   self._threads = []
   for n in range(self._thread_count):
    abort = Event()
    idle  = Event()
    self._aborts.append(abort)
    self._idles.append(idle)
    self._threads.append(QueueWorker(n, self._queue, abort, idle, self._settings))
   return True

 def enqueue_function(self, aFunction, **kwargs):
  args = {'function':aFunction}
  args.update(kwargs)
  self._queue.put(args)

 def enqueue_task(self, args):
  try:
   mod = import_module("zdcp.rest.%s"%args['module'])
   mod.__add_globals__({'gSettings':self._settings})
   args['function'] = getattr(mod,args['func'],lambda x: {'THREAD_NOT_OK'})
   self._queue.put(args)
  except: pass

 def join(self):
  self._queue.join()

 def abort(self, aBlock = False):
  for a in self._aborts:
   a.set()
   while aBlock and self.alive():
    sleep(1)

 def alive(self):
  return True in [t.is_alive() for t in self._threads]

 def idle(self):
  return False not in [i.is_set() for i in self._idles]

 def done(self):
  return self._queue.empty()

 def activities(self):
  return [(t.name,t.is_alive(),t._current) for t in self._threads]

 def size(self):
  return self._queue.qsize()

#
#
class QueueWorker(Thread):
 def __init__(self, aNumber, aQueue, aAbort, aIdle, aSettings):
  from zdcp.core.common import log
  Thread.__init__(self)
  self._n      = aNumber
  self.name    = "QueueWorker(%s)"%aNumber  
  self._queue  = aQueue
  self._abort  = aAbort
  self._idle   = aIdle
  self._idle.set()
  self._settings= aSettings
  self._result = None
  self._current= None
  self._log    = log
  self.daemon  = True
  self.start()

 def run(self):
  while not self._abort.is_set():
   self._idle.set()
   context = self._queue.get(True)
   self._idle.clear()
   try:
    self._current = context.get('id','T')
    if not context.get('periodic'):
     self._result = context['function'](context['args'])
    else:
     freq = int(context.get('frequency',300))
     sleep(freq - int(time())%freq)
     while not self._abort.is_set():
      self._result = context['function'](context['args'])
      if context.get('output'):
       self._log("%s - %s - %s_%s PERIODIC => %s"%(self.name,self._current,context['module'],context['func'],dumps(self._result)))
      sleep(freq)
    if context.get('output'):
     self._log("%s - %s - %s_%s COMPLETE => %s"%(self.name,self._current,context['module'],context['func'],dumps(self._result)))
   except Exception as e:
    self._log("%s - ERROR => %s"%(self.name,str(e)))
   finally:
    self._queue.task_done()
    self._current = None

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
  from zdcp.core.common import DB
  BaseHTTPRequestHandler.timeout  = 60
  httpd = HTTPServer(self._context['address'], SessionHandler, False)
  httpd._path     = self._context['path']
  httpd._node     = self._context['node']
  httpd._settings = self._context['gSettings']
  httpd._workers  = self._context['gWorkers']
  httpd.socket    = self._context['socket']
  httpd._db       = DB()
  httpd._t_id     = self.name
  httpd.server_bind = self.server_close = lambda self: None
  try: httpd.serve_forever()
  except: pass
  return False

###################################### Call Handler ######################################
#
class SessionHandler(BaseHTTPRequestHandler):

 def __init__(self, *args, **kwargs):
  self._headers = {}
  self._body = 'null'
  self.db = args[2]._db
  BaseHTTPRequestHandler.__init__(self,*args, **kwargs)

 def header(self):
  # Sends X-Code as response
  self._headers.update({'X-Thread':self.server._t_id,'X-Method':self.command,'X-Version':__version__,'Server':'ZDCP','Date':self.date_time_string()})
  code = self._headers.pop('X-Code',200)
  self.wfile.write("HTTP/1.1 %s %s\r\n"%(code,http_codes[code]))
  self._headers.update({'Content-Length':len(self._body),'Connection':'close'})
  for k,v in self._headers.iteritems():
   self.send_header(k,v)
  self.end_headers()

 def do_GET(self):
  self.process()
  self.header()
  self.wfile.write(self._body)

 def do_POST(self):
  self.process()
  self.header()
  self.wfile.write(self._body)

 def process(self):
  """ Route request to the right function """
  path,_,query = (self.path.lstrip('/')).partition('/')
  if path == 'site':
   self.site(query)
  elif path == 'api':
   self.api(query)
  elif path == 'debug':
   self.debug(query)
  elif path == 'infra' or path == 'images' or path == 'files':
   self.files(path,query)
  elif path == 'auth':
   self.auth()
  elif path == 'register':
   self.register()
  else:
   # Redirect to login... OR show a list of options 'api/site/...'
   self._headers.update({'Location':'site/system_login?application=%s'%self.server._settings['system'].get('application','system'),'X-Code':301})

 #
 #
 def api(self,query):
  extras = {}
  (api,_,get) = query.partition('?')
  (mod,_,fun) = api.partition('_')
  if get:
   for part in get.split("&"):
    (k,_,v) = part.partition('=')
    extras[k] = v
  self._headers.update({'X-Module':mod, 'X-Function': fun,'Content-Type':"application/json; charset=utf-8",'Access-Control-Allow-Origin':"*",'X-Proc':'API'})
  self._headers['X-Node'] = extras.get('node',self.server._node if not mod == 'system' else 'master')
  try:
   length = int(self.headers.getheader('content-length'))
   args = loads(self.rfile.read(length)) if length > 0 else {}
  except: args = {}
  if extras.get('log','true') == 'true':
   try:
    with open(self.server._settings['logs']['rest'], 'a') as f:
     f.write(unicode("%s: %s '%s' @%s(%s)\n"%(strftime('%Y-%m-%d %H:%M:%S', localtime()), api, dumps(args) if api <> "system_task_worker" else "N/A", self.server._node, get.strip())))
   except: pass
  try:
   if self._headers['X-Node'] == self.server._node:
    module = import_module("zdcp.rest.%s"%mod)
    module.__add_globals__({'gWorkers':self.server._workers,'gSettings':self.server._settings})
    self._body = dumps(getattr(module,fun,None)(args))
   else:
    req  = Request("%s/api/%s"%(self.server._settings['nodes'][self._headers['X-Node']],query), headers = { 'Content-Type': 'application/json','Accept':'application/json' }, data = dumps(args))
    try: sock = urlopen(req, timeout = 300)
    except HTTPError as h:
     raw = h.read()
     try:    data = loads(raw)
     except: data = raw
     self._headers.update({ 'X-Exception':'HTTPError', 'X-Code':h.code, 'X-Info':dumps(dict(h.info())), 'X-Data':data })
    except URLError  as e: self._headers.update({ 'X-Exception':'URLError', 'X-Code':590, 'X-Info':str(e)})
    except Exception as e: self._headers.update({ 'X-Exception':type(e).__name__, 'X-Code':591, 'X-Info':str(e)})
    else:
     try: self._body = sock.read()
     except: pass
     sock.close()
  except Exception as e:
   self._headers.update({'X-Args':args,'X-Info':str(e),'X-Exception':type(e).__name__,'X-Code':500})

 #
 #
 def debug(self,query):
  extras = {}
  (api,_,get) = query.partition('&')
  (mod,_,fun) = api.partition('_')
  if get:
   for part in get.split("&"):
    (k,_,v) = part.partition('=')
    extras[k] = v
  self._headers.update({'X-Module':mod, 'X-Function': fun,'Content-Type':"application/json; charset=utf-8",'Access-Control-Allow-Origin':"*",'X-Proc':'API'})
  self._headers['X-Node'] = extras.get('node',self.server._node if not mod == 'system' else 'master')
  try:
   length = int(self.headers.getheader('content-length'))
   args = loads(self.rfile.read(length)) if length > 0 else {}
  except: args = {}
  if self._headers['X-Node'] == self.server._node:
   module = import_module("zdcp.rest.%s"%mod)
   module.__add_globals__({'gWorkers':self.server._workers,'gSettings':self.server._settings})
   self._body = dumps(getattr(module,fun,None)(args))
  else:
   req  = Request("%s/api/%s"%(self.server._settings['nodes'][self._headers['X-Node']],query), headers = { 'Content-Type': 'application/json','Accept':'application/json' }, data = dumps(args))
   sock = urlopen(req, timeout = 300)
   try: self._body = sock.read()
   except: pass
   sock.close()

 #
 #
 def site(self,query):
  api,_,get = query.partition('?')
  (mod,_,fun)    = api.partition('_')
  stream = Stream(self,get)
  self._headers.update({'Content-Type':'text/html; charset=utf-8','X-Code':200,'X-Proc':'site'})
  #if True:
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
  self._body = stream.output()

 #
 #
 def files(self,path,query):
  query = unquote(query)
  # Infra call
  self._headers['X-Proc'] = 'infra'
  if query.endswith(".js"):
   self._headers['Content-type']='application/javascript; charset=utf-8'
  elif query.endswith(".css"):
   self._headers['Content-type']='text/css; charset=utf-8'
  try:
   if path == 'files':
    param,_,file = query.partition('/')
    fullpath = ospath.join(self.server._settings['files'][param],file)
   else:
    fullpath = ospath.join(self.server._path,path,query)
   if fullpath.endswith("/"):
    self._headers['Content-type']='text/html; charset=utf-8'
    _, _, filelist = next(walk(fullpath), (None, None, []))
    self._body = "<BR>".join(["<A HREF='{0}'>{0}</A>".format(file) for file in filelist])
   else:
    with open(fullpath, 'rb') as file:
     self._body = file.read()
  except Exception as e:
   self._headers.update({'X-Exception':str(e),'X-Query':query,'X-Path':path,'Content-type':'text/html; charset=utf-8','X-Code':404})

 #
 #
 def auth(self):
  self._headers.update({'Content-type':'application/json; charset=utf-8','X-Proc':'auth'})
  try:
   length = int(self.headers.getheader('content-length'))
   args = loads(self.rfile.read(length)) if length > 0 else {}
   # Replace with module load and provide correct headers from system_login
   # There has to be a format for return function of application/authenticate
   self._body = '"OK"'
   self._headers['X-Auth-Token']  = random_string(16)
   self._headers['X-Auth-Expire'] = (datetime.utcnow() + timedelta(days=30)).strftime("%a, %d %b %Y %H:%M:%S GMT")
  except:
   self._body = '"NOT_OK"'

 #
 #
 def register(self):
  """ Register a new node, using node(name), port and system, assume for now that system nodes runs http and not https(!) """
  self._headers.update({'Content-type':'application/json; charset=utf-8','X-Proc':'register'})
  try:
   length = int(self.headers.getheader('content-length'))
   args = loads(self.rfile.read(length)) if length > 0 else {}
   params = {'node':args['node'],'url':"http://%s:%s"%(self.client_address[0],args['port']),'system':args.get('system','0')}
   with self.db:
    update = db.insert_dict('nodes',params,"ON DUPLICATE KEY UPDATE system = %(system)s, url = '%(url)s'"%params)
   self._body = '{"update":%s,"success":true}'%update
  except Exception as e:
   self._body = '{"update":0,"error":"%s"}'%str(e)

########################################### Web stream ########################################
#

class Stream(object):

 def __init__(self,aHandler, aGet):
  self._cookies = {}
  self._form    = {}
  self._node    = aHandler.server._node
  self._api     = aHandler.server._settings['nodes'][self._node]
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
  return " ".join(["<A CLASS='btn z-op small'"," ".join(list("%s='%s'"%(key,value) for key,value in kwargs.iteritems())),"><IMG SRC='../images/btn-%s.png'></A>"%(aImg)])

 # Simplified SDCP REST call
 def rest_call(self, aAPI, aArgs = None, aTimeout = 60):
  from common import rest_call
  return rest_call("%s/api/%s"%(self._api,aAPI), aArgs, aTimeout = 60)['data']

 # Generic REST call with full output
 def rest_full(self, aURL, aArgs = None, aMethod = None, aHeader = None, aTimeout = 20):
  from common import rest_call
  return rest_call(aURL, aArgs, aMethod, aHeader, True, aTimeout)

 def put_html(self, aTitle = None, aIcon = 'zdcp.png'):
  self._body.append("<!DOCTYPE html><HEAD><META CHARSET='UTF-8'><LINK REL='stylesheet' TYPE='text/css' HREF='../infra/4.21.0.vis.min.css' /><LINK REL='stylesheet' TYPE='text/css' HREF='../infra/zdcp.css'>")
  if aTitle:
   self._body.append("<TITLE>" + aTitle + "</TITLE>")
  self._body.append("<LINK REL='shortcut icon' TYPE='image/png' HREF='../images/%s'/>"%(aIcon))
  self._body.append("<SCRIPT SRC='../infra/3.1.1.jquery.min.js'></SCRIPT><SCRIPT SRC='../infra/4.21.0.vis.min.js'></SCRIPT><SCRIPT SRC='../infra/zdcp.js'></SCRIPT>")
  self._body.append("<SCRIPT>$(function() { $(document.body).on('click','.z-op',btn ) .on('focusin focusout','input, select',focus ) .on('input','.slider',slide_monitor); });</SCRIPT>")
  self._body.append("</HEAD>")
