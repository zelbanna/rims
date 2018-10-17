"""System engine"""
__author__ = "Zacharias El Banna"
__version__ = "5.4"
__status__ = "Production"

from os import walk, getpid, path as ospath
from json import loads, load, dumps
from importlib import import_module, reload as reload_module
from threading import Thread, Event, BoundedSemaphore
from time import localtime, strftime, time, sleep
from http.server import BaseHTTPRequestHandler
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.parse import unquote

######################################### Run ########################################
#
# TODO: make multiprocessing - preforking - and multithreaded
#
# - http://stupidpythonideas.blogspot.com/2014/09/sockets-and-multiprocessing.html
# - https://stackoverflow.com/questions/1293652/accept-with-sockets-shared-between-multiple-processes-based-on-apache-prefork
#
# - Manager.dict for settings
#
def run(aSettingsFile):
 """ run instantiate all engine entities and starts monitoring of socket """
 from sys import exit, setcheckinterval
 from signal import signal, SIGINT, SIGUSR1, SIGUSR2
 from .common import rest_call, DB

 kill = Event()
 ctx = None

 def signal_handler(sig,frame):
  if   sig == SIGINT:
   """ TODO clean up and close all DB connections and close socket """
   ctx.workers.abort()
   ctx.sock.close()
   kill.set()
  elif sig == SIGUSR1:
   """ Reload modules and print which ones """
   print("\n".join(ctx.module_reload()))
  elif sig == SIGUSR2:
   """ Print imported external modules """
   print(dumps({k:repr(v) for k,v in ctx.modules.items()},indent=4, sort_keys=True))

 for sig in [SIGINT, SIGUSR1, SIGUSR2]:
  signal(sig, signal_handler)
 setcheckinterval(200)

 try:
  settings = {}
  with open(aSettingsFile,'r') as settings_file:
   settings = load(settings_file)
  settings['system']['config_file'] = aSettingsFile

  ctx = Context(settings)
  ctx.database_create()

  if settings['system']['id'] == 'master':
   extra = ctx.database_settings('master')
   with ctx.db as db:
    db.do("SELECT * FROM tasks LEFT JOIN nodes ON tasks.node_id = nodes.id WHERE node = 'master'")
    tasks = db.get_rows()
  else:
   extra = rest_call("%s/settings/fetch/%s"%(settings['system']['master'],node))['data']['settings']
   tasks = rest_call("%s/api/system_task_list"%settings['system']['master'],{'node':node})['data']['tasks']

  for section,data in extra.items():
   if not settings.get(section):
    settings[section] = {}
   for param, value in data.items():
    settings[section][param] = value

  for task in tasks:
   task.update({'args':loads(task['args']),'output':(task['output'] == 1 or task['output'] == True)})
   frequency = task.pop('frequency',300)
   ctx.workers.add_periodic(task,frequency)

  ctx.run()

 except Exception as e:
  print(str(e))
  try: sock.close()
  except:pass
 else:
  print(getpid())
  kill.wait()
 exit(0)

########################################### Context ########################################
#
# Main state object, contains settings, workers, modules and calls
#

class Context(object):

 def __init__(self,aSettings):
  from .common import rest_call
  self.db       = None
  self.sock     = None
  self.node     = aSettings['system']['id']
  self.settings = aSettings
  self.workers  = WorkerPool(aSettings['system'].get('workers',20),self)
  self.modules  = {}
  self.servers  = None
  self.rest_call = rest_call

 def __str__(self):
  return "Context(%s)"%(self.node)

 def clone(self):
  from copy import copy
  return copy(self)

 def database_create(self):
  from .common import DB
  self.db = DB(self.settings['system']['db_name'],self.settings['system']['db_host'],self.settings['system']['db_user'],self.settings['system']['db_pass']) if self.node == 'master' else None

 def database_settings(self,aNode):
  settings = {}
  with self.db as db:
   db.do("SELECT section,parameter,value FROM settings WHERE node = '%s'"%aNode)
   data = db.get_rows()
   db.do("SELECT 'nodes' AS section, node AS parameter, url AS value FROM nodes")
   data.extend(db.get_rows())
  for param in data:
   section = param.pop('section',None)
   if not settings.get(section):
    settings[section] = {}
   settings[section][param['parameter']] = param['value']
  return settings

 def run(self):
  from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
  addr = ("", int(self.settings['system']['port']))
  self.sock = socket(AF_INET, SOCK_STREAM)
  self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
  self.sock.bind(addr)
  self.sock.listen(5)
  servers = [ServerWorker(n,addr,self.sock,ospath.abspath(ospath.join(ospath.dirname(__file__), '..')),self) for n in range(5)]
  self.workers.run(self)

 def node_call(self, aNode, aModule, aFunction, aArgs = None):
  if self.node != aNode:
   ret = self.rest_call("%s/api/%s_%s"%(self.settings['nodes'][aNode],aModule,aFunction),aArgs)['data']
  else:
   module = import_module("zdcp.rest.%s"%aModule)
   fun = getattr(module,aFunction,None)
   ret = fun(aArgs if aArgs else {},self)
  return ret

 def module_register(self, aName):
  ret = {'import':'error'}
  try:   module = import_module(aName)
  except Exception as e: ret['error'] = str(e)
  else:
   self.modules[aName] = module
   ret['import'] = repr(module)
  return ret

 def module_reload(self):
  from sys import modules as sys_modules
  from types import ModuleType
  modules = {x:sys_modules[x] for x in sys_modules.keys() if x.startswith('zdcp.')}
  modules.update(self.modules)
  ret = []
  for k,v in modules.items():
   if isinstance(v,ModuleType):
    try: reload_module(v)
    except: pass
    else:   ret.append(k)
  ret.sort()
  return ret

########################################## WorkerPool ########################################
#
#
class WorkerPool(object):

 def __init__(self, aThreads, aContext):
  from queue import Queue
  self._queue     = Queue(0)
  self._thread_count = aThreads
  self._ctx       = aContext
  self._abort     = Event()
  self._idles     = []
  self._threads   = []
  self._scheduler = []

 def run(self, aContext):
  for n in range(self._thread_count):
   idle  = Event()
   self._idles.append(idle)
   self._threads.append(QueueWorker(n, self._abort, idle, aContext))

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
   self._queue.put((func,'TASK',aSema,aTask['args'],{'output':aTask['output']}))

 def add_periodic(self, aTask, aFrequency):
  try:
   mod = import_module("zdcp.rest.%s"%aTask['module'])
   func = getattr(mod,aTask['func'],None)
  except: pass
  else:   self._scheduler.append(ScheduleWorker(aFrequency, func, aTask, self._queue, self._abort))

 def abort(self): self._abort.set()

 def join(self): self._queue.join()

 def done(self): return self._queue.empty()

 def queue_size(self):return self._queue.qsize()

 def pool_size(self): return self._thread_count

 def scheduler_size(self): return len(self._scheduler)

 def semaphore(self,aSize): return BoundedSemaphore(aSize)

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
  self._args  = aTask['args']
  self._output= {'output':aTask['output']}
  self.daemon = True
  self.name   = "ScheduleWorker(%s,%s)"%(aTask['id'],self._freq)
  self.start()

 def run(self):
  sleep(self._freq - int(time())%self._freq)
  while not self._abort.is_set():
   self._queue.put((self._func,'TASK',None,self._args,self._output))
   sleep(self._freq)
  return False

#
#
class QueueWorker(Thread):

 def __init__(self, aNumber, aAbort, aIdle, aContext):
  Thread.__init__(self)
  self._n      = aNumber
  self.name    = "QueueWorker(%02d)"%aNumber
  self._abort  = aAbort
  self._idle   = aIdle
  self._ctx    = aContext.clone()
  self._ctx.database_create()
  self._queue  = self._ctx.workers._queue
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
      log("%s - %s => %s"%(self.name,repr(func),dumps(result)), self._ctx.settings['logs']['system'])
   except Exception as e:
    log("%s - ERROR => %s"%(self.name,str(e)), self._ctx.settings['logs']['system'])
   finally:
    if sema:
     sema.release()
    self._queue.task_done()

#
#
class ServerWorker(Thread):

 def __init__(self, aNumber, aAddress, aSocket, aPath, aContext):
  Thread.__init__(self)
  from http.server import HTTPServer
  self.name    = "ServerWorker(%02d)"%aNumber
  self.daemon  = True
  httpd = HTTPServer(aAddress, SessionHandler, False)
  self._httpd  = httpd
  httpd.socket = aSocket
  httpd._path  = aPath
  httpd._ctx = self._ctx = aContext.clone()
  httpd._ctx.database_create()
  httpd._node  = self._ctx.settings['system']['id']
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
  elif path in ['api','debug','external']:
   self.api(path,query)
  elif path in ['infra','images','files']:
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
   self._headers.update({'Location':'../site/system_login?application=%s'%(self._ctx.settings['system'].get('application','system')),'X-Code':301})

 #
 #
 def api(self,path,query):
  """ API serves the REST functions x.y.z.a:<port>/api|debug|external/module/function"""
  extras = {}
  (api,_,get) = query.partition('?')
  (mod,_,fun) = api.partition('/')
  if get:
   for part in get.split("&"):
    (k,_,v) = part.partition('=')
    extras[k] = v
  self._headers.update({'X-Module':mod, 'X-Function': fun,'Content-Type':"application/json; charset=utf-8",'Access-Control-Allow-Origin':"*",'X-Process':'API'})
  self._headers['X-Node'] = extras.get('node',self._ctx.node if not mod == 'system' else 'master')
  try:
   length = int(self.headers['Content-Length'])
   args = loads(self.rfile.read(length).decode()) if length > 0 else {}
  except: args = {}
  if extras.get('log','true') == 'true':
   try:
    with open(self._ctx.settings['logs']['rest'], 'a') as f:
     f.write(str("%s: %s '%s' @%s(%s)\n"%(strftime('%Y-%m-%d %H:%M:%S', localtime()), api, dumps(args) if api != "system_task_worker" else "N/A", self._ctx.node, get.strip())))
   except: pass
  try:
   if self._headers['X-Node'] == self._ctx.node:
    module = import_module("zdcp.rest.%s"%mod) if not path == 'external' else self._ctx.modules.get(mod)
    self._body = dumps(getattr(module,fun,None)(args,self._ctx)).encode('utf-8')
   else:
    req  = Request("%s/%s/%s"%(self._ctx.settings['nodes'][self._headers['X-Node']],path,query), headers = { 'Content-Type': 'application/json','Accept':'application/json' }, data = dumps(args).encode('utf-8'))
    try: sock = urlopen(req, timeout = 300)
    except HTTPError as h:
     raw = h.read()
     try:    data = loads(raw.decode())
     except: data = raw
     self._headers.update({ 'X-Exception':'HTTPError', 'X-Code':h.code, 'X-Info':dumps(dict(h.info())), 'X-Data':data })
    except Exception as e: self._headers.update({ 'X-Exception':type(e).__name__, 'X-Code':590, 'X-Info':str(e)})
    else:
     try: self._body = sock.read()
     except: pass
     sock.close()
  except Exception as e:
   self._headers.update({'X-Args':args,'X-Info':str(e),'X-Exception':type(e).__name__,'X-Code':500})
   if extras.get('debug') or path == 'debug':
    from traceback import format_exc
    tb = format_exc()
    if extras.get('debug') == 'print':
     print(tb)
    else:
     for n,v in enumerate(tb.split('\n')):
      self._headers["X-Debug-%02d"%n] = v

 #
 #
 def site(self,query):
  """ Site - serve AJAX information """
  api,_,get = query.partition('?')
  (mod,_,fun)    = api.partition('_')
  stream = Stream(self,get)
  self._headers.update({'Content-Type':'text/html; charset=utf-8','X-Code':200,'X-Process':'site'})
  try:
   module = import_module("zdcp.site.%s"%mod)
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
    fullpath = ospath.join(self._ctx.settings['files'][param],file)
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
   self._body = b'OK'
   self._headers['X-Auth-Token']  = random_string(16)
   self._headers['X-Auth-Expire'] = (datetime.utcnow() + timedelta(days=30)).strftime("%a, %d %b %Y %H:%M:%S GMT")
  except:
   self._body = b'NOT_OK'

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
   self._body = dumps({'update':0,'error':str(e),'info':"Function is called by node to register its URL and port into 'node' repository"}).encode('utf-8')

 #
 #
 def reload(self,query):
  """ Reload imported (system) modules """
  self._headers.update({'Content-type':'application/json; charset=utf-8','X-Process':'reload'})
  res = self._ctx.module_reload()
  self._body = dumps({'modules':res}).encode('utf-8')

 #
 #
 def settings(self,query):
  """ /settings/<op>/<node> """
  self._headers.update({'Content-type':'application/json; charset=utf-8','X-Process':'settings'})
  op,_,node = query.partition('/')
  if self._ctx.settings['system']['id'] == 'master' and (op == 'fetch' or (op == 'sync' and node != 'master')):
   settings = self._ctx.database_settings(node)
   if op == 'fetch':
    output = {'settings':settings}
   else:
    req  = Request("%s/settings/update"%(self._ctx.settings['nodes'][node]), headers = { 'Content-Type': 'application/json','Accept':'application/json'}, data = dumps(settings).encode('utf-8'))
    try: sock = urlopen(req, timeout = 300)
    except Exception as e:
     self._headers.update({ 'X-Exception':type(e).__name__, 'X-Code':590, 'X-Info':str(e)})
     output = {'node':node,'result':'SYNC_NOT_OK'}
    else:
     output = {'node':node,'result':'SYNC_OK'}
  elif op == 'update':
   length   = int(self.headers['Content-Length'])
   settings = self._ctx.settings
   filename = settings['system']['config_file']
   settings.clear()
   settings.update(loads(self.rfile.read(length).decode()) if length > 0 else {})
   with open(filename,'r') as settings_file:
    settings.update(load(settings_file))
   settings['system']['config_file'] = filename
   output = 'UPDATE_OK'
  elif op == 'show':
   output = self._ctx.settings
  else:
   output = {'result':'SETTINGS_NOT_OK','info':'settings/<show|fetch|sync>/<node> where fetch and sync runs on master node'}
  self._body = dumps(output).encode('utf-8')

########################################### Web stream ########################################
#

class Stream(object):

 def __init__(self,aHandler, aGet):
  self._form = {}
  self._node = aHandler._ctx.node
  self._api  = aHandler._ctx.settings['nodes'][self._node]
  self._body = []
  self._cookies   = {}
  self._rest_call = aHandler._ctx.rest_call
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

 def get_args(self,aExcept = []):
  return "&".join("%s=%s"%(k,v) for k,v in self._form.items() if not k in aExcept)

 def button(self,aImg,**kwargs):
  return "<A CLASS='btn z-op small' " + " ".join("%s='%s'"%i for i in kwargs.items()) + "><IMG SRC='../images/btn-%s.png'></A>"%(aImg)

 def rest_call(self, aAPI, aArgs = None, aTimeout = 60):
  return self._rest_call("%s/api/%s"%(self._api,aAPI), aArgs, aTimeout = 60)['data']

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
