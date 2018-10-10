"""System engine"""
__author__ = "Zacharias El Banna"
__version__ = "5.1GA"
__status__ = "Production"

from os import walk, path as ospath
from json import loads, load, dumps
from importlib import import_module, reload
from threading import Thread, Event, BoundedSemaphore
from time import localtime, strftime, time, sleep
from http.server import BaseHTTPRequestHandler
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.parse import unquote

######################################### Run ########################################
#
# Single process server, multiple threads to avoid blocking
#
# TODO: make multicore instead
#
def run(aSettingsFile):
 """ run instantiate all engine entities """
 from sys import exit, setcheckinterval
 from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
 from signal import signal, SIGINT, SIGUSR1
 from .common import rest_call, DB

 kill = Event()

 def signal_handler(sig,frame):
  if   sig == SIGINT:
   """ TODO clean up and close all DB connections and close socket """
   sock.close()
   kill.set()
  elif sig == SIGUSR1:
   """ Catch SIGUSR1 and reload all modules """
   from sys import modules as sys_modules
   from types import ModuleType
   modules = {x:False for x in sys_modules.keys() if x.startswith('zdcp.')}
   for m in modules.keys():
    mod = sys_modules.get(m,None)
    if isinstance(mod,ModuleType):
     try: reload(mod)
     except: pass
     else:   modules[m] = True
   print(dumps(modules,indent=4,sort_keys=True))

 signal(SIGINT, signal_handler)
 signal(SIGUSR1,signal_handler)
 setcheckinterval(200)

 try:
  settings = {}
  with open(aSettingsFile,'r') as settings_file:
   data = load(settings_file)
  for section,params in data.items():
   if not settings.get(section):
    settings[section] = {}
   for param,info in params.items():
    settings[section][param] = info['value']

  node = settings['system']['id']
  addr = ("", int(settings['system']['port']))
  sock = socket(AF_INET, SOCK_STREAM)
  sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
  sock.bind(addr)
  sock.listen(5)

  if node == 'master':
   with DB() as db:
    db.do("SELECT section,parameter,value FROM settings WHERE node = 'master'")
    data = db.get_rows()
    db.do("SELECT 'nodes' AS section, node AS parameter, url AS value FROM nodes")
    data.extend(db.get_rows())
    db.do("SELECT * FROM tasks LEFT JOIN nodes ON tasks.node_id = nodes.id WHERE node = 'master'")
    tasks = db.get_rows()
   for param in data:
    section = param.pop('section',None)
    if not settings.get(section):
     settings[section] = {}
    settings[section][param['parameter']] = param['value']
   settings['system']['config_file'] = aSettingsFile

   workers = WorkerPool(settings['system'].get('workers',20),settings)
   servers = [ServerWorker(n,addr,sock,ospath.abspath(ospath.join(ospath.dirname(__file__), '..')),settings,workers) for n in range(5)]

   for task in tasks:
    task.update({'args':loads(task['args']),'output':(task['output'] == 1)})
    frequency = task.pop('frequency',300)
    workers.add_periodic(task,frequency)
  else:
   extra = rest_call("%s/settings/fetch/%s"%(settings['system']['master'],node))['data']['settings']
   settings.update(extra)
   tasks = rest_call("%s/api/system_task_list"%settings['system']['master'],{'node':node})['data']['tasks']
   for task in tasks:
    task['args'] = loads(task['args'])
    frequency = task.pop('frequency',300)
    workers.add_periodic(task,frequency)
 except Exception as e:
  print(str(e))
  try:   sock.close()
  except:pass
 else:
  kill.wait()
 exit(0)

########################################### Context ########################################
#

class Context(object):

 def __init__(self,aSettings, aWorkers):
  from .common import DB, rest_call
  self.node      = aSettings['system']['id']
  self.settings  = aSettings
  self.workers   = aWorkers
  self.db        = DB() if self.node == 'master' else None
  self.rest_call = rest_call
  self.handler   = None

 def set_handler(self,aHandler):
  self.handler = aHandler

 def node_call(self, aNode, aModule, aFunction, aArgs = None):
  if self.node != aNode:
   ret = self.rest_call("%s/api/%s_%s"%(self.settings['nodes'][aNode],aModule,aFunction),aArgs)['data']
  else:
   module = import_module("zdcp.rest.%s"%aModule)
   fun = getattr(module,aFunction,None)
   ret = fun(aArgs if aArgs else {},self)
  return ret

########################################## WorkerPool ########################################
#
#
class WorkerPool(object):

 def __init__(self, aThreadCount, aSettings):
  from queue import Queue
  self._queue = Queue(0)
  self._thread_count = aThreadCount
  self._abort = Event()
  self._idles = []
  self._threads   = []
  self._scheduler = []
  self._settings  = aSettings
  for n in range(self._thread_count):
   idle  = Event()
   self._idles.append(idle)
   self._threads.append(QueueWorker(n, self._settings, self, self._abort, idle))

 def __str__(self):
  return "WorkerPool(%s):[%s,%s]"%(self._thread_count,self._queue.qsize(),len(self._scheduler))

 def add_function(self, aFunction, *args, **kwargs):
  self._queue.put((aFunction,'FUNCTION',None,args,kwargs))

 def add_semaphore(self, aFunction, aSema, *args, **kwargs):
  aSema.acquire()
  self._queue.put((aFunction,'FUNCTION',aSema,args,kwargs))

 def add_transient(self, aTask, aSema = None):
  try:
   mod = import_module("zdcp.rest.%s"%aTask['module'])
   func = getattr(mod,aTask['func'],None)
  except: pass
  else:
   if aSema:
    aSema.acquire()
   self._queue.put((func,'TASK',aSema,aTask.pop('args',None),aTask))

 def add_periodic(self, aTask, aFrequency):
  try:
   mod = import_module("zdcp.rest.%s"%aTask['module'])
   func = getattr(mod,aTask['func'],None)
  except: pass
  else:
   self._scheduler.append(ScheduleWorker(aFrequency, func, aTask, self._queue, self._abort))

 def abort(self):
  self._abort.set()

 def join(self):
  self._queue.join()

 def done(self):
  return self._queue.empty()

 def queue_size(self):
  return self._queue.qsize()

 def pool_size(self):
  return self._thread_count

 def scheduler_size(self):
  return len(self._scheduler)

 def semaphore(self,aSize):
  return BoundedSemaphore(aSize)  

 def block(self,aSema,aSize):
  for i in range(aSize):
   aSema.acquire()
 
###################################### Threads ########################################
#

class ScheduleWorker(Thread):

 def __init__(self, aFrequency, aFunc, aTask, aQueue, aAbort):
  Thread.__init__(self)
  self._freq  = aFrequency
  self._queue = aQueue
  self._abort = aAbort
  self._func  = aFunc
  self._args  = aTask.pop('args',None)
  self._task  = aTask
  self.daemon = True
  self.name   = "ScheduleWorker(%s,%s)"%(aTask['id'],self._freq)
  self.start()

 def run(self):
  sleep(self._freq - int(time())%self._freq)
  while not self._abort.is_set():
   self._queue.put((self._func,'TASK',None,self._args,self._task))
   sleep(self._freq)
  return False

#
#
class QueueWorker(Thread):

 def __init__(self, aNumber, aSettings, aWorkers, aAbort, aIdle):
  Thread.__init__(self)
  self._n      = aNumber
  self.name    = "QueueWorker(%02d)"%aNumber
  self._queue  = aWorkers._queue
  self._abort  = aAbort
  self._idle   = aIdle
  self._ctx    = Context(aSettings,aWorkers)
  self.daemon  = True
  self.start()

 def run(self):
  from .common import log
  while not self._abort.is_set():
   try:
    self._idle.set()
    func, mode, sema, args, kwargs = self._queue.get(True)
    self._idle.clear()
    if mode == 'FUNCTION':
     result = func(*args,**kwargs)
    else:
     result = func(args,self._ctx)
     if kwargs.get('output'):
      log("%s - %s_%s => %s"%(self.name,kwargs['module'],kwargs['func'],dumps(result)))
   except Exception as e:
    log("%s - ERROR => %s"%(self.name,str(e)))
   finally:
    if sema:
     sema.release()
    self._queue.task_done()

#
#
class ServerWorker(Thread):

 def __init__(self, aNumber, aAddress, aSocket, aPath, aSettings, aWorkers):
  Thread.__init__(self)
  from http.server import HTTPServer
  self.name   = "ServerWorker(%02d)"%aNumber
  self.daemon = True
  httpd = HTTPServer(aAddress, SessionHandler, False)
  self._httpd = httpd
  httpd.socket = aSocket
  httpd._path  = aPath
  httpd._node  = aSettings['system']['id']
  self._ctx = httpd._ctx = Context(aSettings,aWorkers)
  httpd.server_bind = httpd.server_close = lambda self: None
  self.start()
  
 def run(self):
  try: self._httpd.serve_forever()
  except: pass

###################################### Call Handler ######################################
#
class SessionHandler(BaseHTTPRequestHandler):

 def __init__(self, *args, **kwargs):
  self._headers = {}
  self._body    = b'null'
  self._ctx     = args[2]._ctx
  BaseHTTPRequestHandler.__init__(self,*args, **kwargs)

 def header(self):
  # Sends X-Code as response
  self._headers.update({'X-Method':self.command,'Server':'Engine %s'%__version__,'Date':self.date_time_string()})
  code = self._headers.pop('X-Code',200)
  self.wfile.write(('HTTP/1.1 %s %s\r\n'%(code,self.responses.get(code,('Other','Server specialized return code'))[0])).encode('utf-8'))
  self._headers.update({'Content-Length':len(self._body),'Connection':'close'})
  for k,v in self._headers.items():
   self.send_header(k,v)
  self.end_headers()

 def do_GET(self):
  self.route()
  self.header()
  self.wfile.write(self._body)

 def do_POST(self):
  self.route()
  self.header()
  self.wfile.write(self._body)

 def route(self):
  """ Route request to the right function """
  path,_,query = (self.path.lstrip('/')).partition('/')
  if path == 'site':
   self.site(query)
  elif path == 'api':
   self.api(query)
  elif path == 'infra' or path == 'images' or path == 'files':
   self.files(path,query)
  elif path == 'auth':
   self.auth()
  elif path == 'register':
   self.register()
  elif path == 'reload':
   self.reload(query)
  elif path == 'settings':
   self.settings(query)
  else:
   # Redirect to login... OR show a list of options 'api/site/...'
   self._headers.update({'Location':'../site/system_login?application=%s'%self.server._ctx.settings['system'].get('application','system'),'X-Code':301})
   self._body = 'null'.encode('utf-8')
 #
 #
 def api(self,query):
  """ API serves the REST functions """
  extras = {}
  (api,_,get) = query.partition('?')
  (mod,_,fun) = api.partition('_')
  if get:
   for part in get.split("&"):
    (k,_,v) = part.partition('=')
    extras[k] = v
  self._headers.update({'X-Module':mod, 'X-Function': fun,'Content-Type':"application/json; charset=utf-8",'Access-Control-Allow-Origin':"*",'X-Process':'API'})
  self._headers['X-Node'] = extras.get('node',self.server._node if not mod == 'system' else 'master')
  try:
   length = int(self.headers['Content-Length'])
   args = loads(self.rfile.read(length).decode()) if length > 0 else {}
  except: args = {}
  if extras.get('log','true') == 'true':
   try:
    with open(self.server._ctx.settings['logs']['rest'], 'a') as f:
     f.write(str("%s: %s '%s' @%s(%s)\n"%(strftime('%Y-%m-%d %H:%M:%S', localtime()), api, dumps(args) if api != "system_task_worker" else "N/A", self.server._node, get.strip())))
   except: pass
  try:
   if self._headers['X-Node'] == self.server._node:
    module = import_module("zdcp.rest.%s"%mod)
    self._body = dumps(getattr(module,fun,None)(args,self.server._ctx))
   else:
    req  = Request("%s/api/%s"%(self.server._ctx.settings['nodes'][self._headers['X-Node']],query), headers = { 'Content-Type': 'application/json','Accept':'application/json' }, data = dumps(args).encode('utf-8'))
    try: sock = urlopen(req, timeout = 300)
    except HTTPError as h:
     raw = h.read()
     try:    data = loads(raw.decode())
     except: data = raw
     self._headers.update({ 'X-Exception':'HTTPError', 'X-Code':h.code, 'X-Info':dumps(dict(h.info())), 'X-Data':data })
    except Exception as e: self._headers.update({ 'X-Exception':type(e).__name__, 'X-Code':590, 'X-Info':str(e)})
    else:
     try: self._body = sock.read().decode()
     except: pass
     sock.close()
  except Exception as e:
   self._headers.update({'X-Args':args,'X-Info':str(e),'X-Exception':type(e).__name__,'X-Code':500})
   if extras.get('debug'):
    from traceback import format_exc
    tb = format_exc()
    if extras['debug'] == 'print':
     print(tb)
    else:
     for n,v in enumerate(tb.split('\n')):
      self._headers["X-Debug-%02d"%n] = v
  self._body = self._body.encode('utf-8')

 #
 #
 def site(self,query):
  """ Site - serve AJAX information """
  api,_,get = query.partition('?')
  (mod,_,fun)    = api.partition('_')
  stream = Stream(self,get)
  self._headers.update({'Content-Type':'text/html; charset=utf-8','X-Code':200,'X-Process':'site'})
  try:
   module = import_module("zdcp.site." + mod)
   getattr(module,fun,None)(stream)
  except Exception as e:
   stream.wr("<DETAILS CLASS='web'><SUMMARY CLASS='red'>ERROR</SUMMARY>API:&nbsp; zdcp.site.%s_%s<BR>"%(mod,fun))
   try:
    stream.wr("Type: %s<BR>Code: %s<BR><DETAILS open='open'><SUMMARY>Info</SUMMARY>"%(e[0]['exception'],e[0]['code']))
    try:
     for i in e[0]['info'].items():
      stream.wr("%s: %s<BR>"%i)
    except: stream.wr(e[0]['info'])
    stream.wr("</DETAILS>")
   except:
    stream.wr("Type: %s<BR><DETAILS open='open'><SUMMARY>Info</SUMMARY><CODE>%s</CODE></DETAILS>"%(type(e).__name__,str(e)))
   stream.wr("<DETAILS><SUMMARY>Args</SUMMARY><CODE>%s</CODE></DETAILS>"%(",".join(stream._form.keys())))
   stream.wr("<DETAILS><SUMMARY>Cookie</SUMMARY><CODE>%s</CODE></DETAILS></DETAILS>"%(stream._cookies))
  self._body = stream.output().encode('utf-8')

 #
 #
 def files(self,path,query):
  """ Serve "common" system files and also route 'files' """
  query = unquote(query)
  # Infra call
  self._headers['X-Process'] = 'infra'
  if query.endswith(".js"):
   self._headers['Content-type']='application/javascript; charset=utf-8'
  elif query.endswith(".css"):
   self._headers['Content-type']='text/css; charset=utf-8'
  try:
   if path == 'files':
    param,_,file = query.partition('/')
    fullpath = ospath.join(self.server._ctx.settings['files'][param],file)
   else:
    fullpath = ospath.join(self.server._path,path,query)
   if fullpath.endswith("/"):
    self._headers['Content-type']='text/html; charset=utf-8'
    _, _, filelist = next(walk(fullpath), (None, None, []))
    self._body = ("<BR>".join("<A HREF='{0}'>{0}</A>".format(file) for file in filelist)).encode('utf-8')
   else:
    with open(fullpath, 'rb') as file:
     self._body = file.read()
  except Exception as e:
   self._headers.update({'X-Exception':str(e),'X-Query':query,'X-Path':path,'Content-type':'text/html; charset=utf-8','X-Code':404})
   self._body = b''

 #
 #
 def auth(self):
  """ Authenticate using node function instead of API - internally wrap this into rest API call bypassing token verification """
  self._headers.update({'Content-type':'application/json; charset=utf-8','X-Process':'auth'})
  try:
   length = int(self.headers['Content-Length'])
   args = loads(self.rfile.read(length).decode()) if length > 0 else {}
   # Replace with module load and provide correct headers from system_login
   # There has to be a format for return function of application/authenticate
   self._body = '"OK"'
   self._headers['X-Auth-Token']  = random_string(16)
   self._headers['X-Auth-Expire'] = (datetime.utcnow() + timedelta(days=30)).strftime("%a, %d %b %Y %H:%M:%S GMT")
  except:
   self._body = '"NOT_OK"'
  self._body = self._body.encode('utf-8')

 #
 #
 def register(self):
  """ Register a new node, using node(name), port and system, assume for now that system nodes runs http and not https(!) """
  self._headers.update({'Content-type':'application/json; charset=utf-8','X-Process':'register'})
  try:
   length = int(self.headers['Content-Length'])
   args = loads(self.rfile.read(length).decode()) if length > 0 else {}
   params = {'node':args['node'],'url':"http://%s:%s"%(self.client_address[0],args['port']),'system':args.get('system','0')}
   with self._ctx.db as db:
    update = db.insert_dict('nodes',params,"ON DUPLICATE KEY UPDATE system = %(system)s, url = '%(url)s'"%params)
   self._body = dumps({'update':update,'success':True}).encode('utf-8')
  except Exception as e:
   self._body = dumps({'update':0,'error':str(e)}).encode('utf-8')

 #
 #
 def reload(self,query):
  """ Reload a system module defined by query: /reload/<path>/<module>"""
  self._headers.update({'Content-type':'application/json; charset=utf-8','X-Process':'reload'})
  from sys import modules as sys_modules
  from types import ModuleType
  module = 'zdcp.%s'%query.replace('/','.')
  modules = {x:False for x in sys_modules.keys() if x.startswith(module)}
  for m in modules.keys():
   mod = sys_modules.get(m,None)
   if isinstance(mod,ModuleType):
    try: reload(mod)
    except: pass
    else:   modules[m] = True
  self._body = dumps({'modules':modules}).encode('utf-8')

 #
 #
 def settings(self,query):
  """ /settings/<op>/<node> """
  self._headers.update({'Content-type':'application/json; charset=utf-8','X-Process':'settings'})  
  op,_,node = query.partition('/')
  if op == 'fetch':
   settings = {}
   with self._ctx.db as db:
    db.do("SELECT section,parameter,value FROM settings WHERE node = '%s'"%node)
    data = db.get_rows()
    db.do("SELECT 'nodes' AS section, node AS parameter, url AS value FROM nodes")
    data.extend(db.get_rows())
   for param in data:
    section = param.pop('section',None)
    if not settings.get(section):
     settings[section] = {}
    settings[section][param['parameter']] = param['value']
   self._body = dumps({'settings':settings}).encode('utf-8')
  elif op == 'update':
   """ On the right node - use settings """
   length = int(self.headers['Content-Length'])
   self._ctx.settings.clear()
   self._ctx.settings.update(loads(self.rfile.read(length).decode()) if length > 0 else {})
   self._body = b'done'

########################################### Web stream ########################################
#

class Stream(object):

 def __init__(self,aHandler, aGet):
  self._form = {}
  self._node = aHandler.server._node
  self._api  = aHandler.server._ctx.settings['nodes'][self._node]
  self._body = []
  self._cookies   = {}
  self._rest_call = aHandler.server._ctx.rest_call
  try: cookie_str = aHandler.headers['Cookie'].split('; ')
  except: pass
  else:
   for cookie in cookie_str:
    k,_,v = cookie.partition('=')
    try:    self._cookies[k] = dict(x.split('=') for x in v.split(','))
    except: self._cookies[k] = v
  try:    body_len = int(aHandler.headers['Content-Length'])
  except: body_len = 0
  if body_len > 0 or len(aGet) > 0:
   from urllib.parse import parse_qs
   if body_len > 0:
    self._form.update({ k: l[0] for k,l in parse_qs(aHandler.rfile.read(body_len).decode(), keep_blank_values=1).items() })
   if len(aGet) > 0:
    self._form.update({ k: l[0] for k,l in parse_qs(aGet, keep_blank_values=1).items() })

 def __str__(self):
  return "<DETAILS CLASS='web blue'><SUMMARY>Web</SUMMARY>Web object<DETAILS><SUMMARY>Cookies</SUMMARY><CODE>%s</CODE></DETAILS><DETAILS><SUMMARY>Form</SUMMARY><CODE>%s</CODE></DETAILS></DETAILS>"%(str(self._cookies),self._form)

 def output(self):
  return ("".join(self._body))

 def wr(self,aHTML):
  self._body.append(aHTML)

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
  return { k:v for k,v in self._form.items() if not k in aExcept }

 def get_args(self,aExcept = []):
  return "&".join("%s=%s"%(k,v) for k,v in self._form.items() if not k in aExcept)

 def button(self,aImg,**kwargs):
  return "<A CLASS='btn z-op small' " + " ".join("%s='%s'"%i for i in kwargs.items()) + "><IMG SRC='../images/btn-%s.png'></A>"%(aImg)

 # Simplified SDCP REST call
 def rest_call(self, aAPI, aArgs = None, aTimeout = 60):
  return self._rest_call("%s/api/%s"%(self._api,aAPI), aArgs, aTimeout = 60)['data']

 # Generic REST call with full output
 def rest_full(self, aURL, aArgs = None, aMethod = None, aHeader = None, aTimeout = 20):
  return self._rest_call(aURL, aArgs, aMethod, aHeader, True, aTimeout)

 def put_html(self, aTitle = None, aIcon = 'zdcp.png'):
  self._body.append("<!DOCTYPE html><HEAD><META CHARSET='UTF-8'><LINK REL='stylesheet' TYPE='text/css' HREF='../infra/4.21.0.vis.min.css' /><LINK REL='stylesheet' TYPE='text/css' HREF='../infra/system.css'>")
  if aTitle:
   self._body.append("<TITLE>" + aTitle + "</TITLE>")
  self._body.append("<LINK REL='shortcut icon' TYPE='image/png' HREF='../images/%s'/>"%(aIcon))
  self._body.append("<SCRIPT SRC='../infra/3.1.1.jquery.min.js'></SCRIPT><SCRIPT SRC='../infra/4.21.0.vis.min.js'></SCRIPT><SCRIPT SRC='../infra/system.js'></SCRIPT>")
  self._body.append("<SCRIPT>$(function() { $(document.body).on('click','.z-op',btn ) .on('focusin focusout','input, select',focus ) .on('input','.slider',slide_monitor); });</SCRIPT>")
  self._body.append("</HEAD>")
