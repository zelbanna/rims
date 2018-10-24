"""System engine"""
__author__ = "Zacharias El Banna"
__version__ = "5.5"
__minor__ = 9

from json import loads, load, dumps
from importlib import import_module, reload as reload_module
from threading import Thread, Event, BoundedSemaphore
from time import localtime, strftime, time, sleep
from http.server import BaseHTTPRequestHandler
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.parse import unquote, parse_qs

########################################### Context ########################################
#
# Main state object, contains settings, workers, modules and calls etc..
#
# TODO: make multiprocessing - preforking - and multithreaded
#
# - http://stupidpythonideas.blogspot.com/2014/09/sockets-and-multiprocessing.html
# - https://stackoverflow.com/questions/1293652/accept-with-sockets-shared-between-multiple-processes-based-on-apache-prefork
# - Manager.dict for settings
#

class Context(object):

 def __init__(self,aConfig = None, aConfigFile = None):
  """ Context init - create the infrastructure but populate later
  - Set node ID
  - Prepare database and workers
  - Load config, i.e. base settings
  - initiate the 'kill' switch
  - create datastore (i.e. dict) for settings, nodes, servers and external modules
  """
  from .common import DB, rest_call
  if not aConfig:
   with open(aConfigFile,'r') as config_file:
    self.config = load(config_file)
    self.config['config_file'] = aConfigFile
  else:
   self.config  = aConfig
  self.node     = self.config['id']
  self.db       = DB(self.config['db_name'],self.config['db_host'],self.config['db_user'],self.config['db_pass']) if self.node == 'master' else None
  self.workers  = WorkerPool(self.config.get('workers',20),self)
  self.kill     = Event()
  self.settings = {}
  self.nodes    = {}
  self.modules  = {}
  self.servers  = {}
  self.sock     = None
  self.rest_call = rest_call

 def __str__(self):
  return "Context(%s)"%(self.node)

 #
 def clone(self):
  """ Clone itself and non thread-safe components """
  from copy import copy
  from .common import DB
  ctx_new = copy(self)
  ctx_new.db = DB(self.config['db_name'],self.config['db_host'],self.config['db_user'],self.config['db_pass']) if self.node == 'master' else None
  return ctx_new

 #
 def wait(self):
  self.kill.wait()

 #
 def system_info(self,aNode):
  nodes, services, settings = {}, {}, {}
  with self.db as db:
   db.do("SELECT section,parameter,value FROM settings WHERE node = '%s'"%aNode)
   data = db.get_rows()
   db.do("SELECT id, node, url FROM nodes")
   node_list = db.get_rows()
   db.do("SELECT id, node, server, type FROM servers")
   services_list = db.get_rows()
   db.do("SELECT tasks.id, user_id, module, func, args, frequency, output FROM tasks LEFT JOIN nodes ON nodes.id = tasks.node_id WHERE node = '%s'"%aNode)
   tasks = db.get_rows()
  for node in node_list:
   name = node.pop('node',None)
   nodes[name] = node
  for svc in services_list:
   id = svc.pop('id',None)
   services[id] = svc
  for task in tasks:
   task['output'] = (task['output']== 1)
  for param in data:
   section = param.pop('section',None)
   if not settings.get(section):
    settings[section] = {}
   settings[section][param['parameter']] = param['value']
  return {'settings':settings,'tasks':tasks,'servers':services,'nodes':nodes}

 #
 def load_system(self):
  """ Load settings from DB or master node and do same with tasks. Add tasks to queue """
  if self.node  == 'master':
   system = self.system_info('master')
  else:
   system = self.rest_call("%s/system/info/%s"%(self.config['master'],self.node))['data']
  self.settings.update(system['settings'])
  self.nodes.update(system['nodes'])
  self.servers.update(system['servers'])
  for task in system['tasks']:
   task.update({'args':loads(task['args']),'output':(task['output'] == 1 or task['output'] == True)})
   frequency = task.pop('frequency',300)
   self.workers.add_periodic(task,frequency)

 #
 def start(self):
  """ Start "moving" parts of context """
  from sys import setcheckinterval
  from os import path as ospath
  from signal import signal, SIGINT, SIGUSR1, SIGUSR2
  from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
  addr = ("", int(self.config['port']))
  self.sock = socket(AF_INET, SOCK_STREAM)
  self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
  self.sock.bind(addr)
  self.sock.listen(5)
  path = ospath.abspath(ospath.join(ospath.dirname(__file__), '..'))
  servers = [ServerWorker(n,addr,self.sock,path,self) for n in range(5)]
  self.workers.run(self)
  for sig in [SIGINT, SIGUSR1, SIGUSR2]:
   signal(sig, self.signal_handler)
  setcheckinterval(200)

 #
 def close(self):
  """ TODO clean up and close all DB connections and close socket """
  self.workers.abort()
  try: self.sock.close()
  except: pass
  self.kill.set()

 #
 def node_call(self, aNode, aModule, aFunction, aArgs = None):
  if self.node != aNode:
   ret = self.rest_call("%s/api/%s_%s"%(self.nodes[aNode]['url'],aModule,aFunction),aArgs)['data']
  else:
   module = import_module("rims.rest.%s"%aModule)
   fun = getattr(module,aFunction,None)
   ret = fun(aArgs if aArgs else {},self)
  return ret

 #
 def module_register(self, aName):
  """ Register "external" modules """
  ret = {'import':'error'}
  try:   module = import_module(aName)
  except Exception as e: ret['error'] = str(e)
  else:
   self.modules[aName] = module
   ret['import'] = repr(module)
  return ret

 #
 def module_reload(self):
  """ Reload modules and return which ones were reloaded """
  from sys import modules as sys_modules
  from types import ModuleType
  modules = {x:sys_modules[x] for x in sys_modules.keys() if x.startswith('rims.')}
  modules.update(self.modules)
  ret = []
  for k,v in modules.items():
   if isinstance(v,ModuleType):
    try: reload_module(v)
    except: pass
    else:   ret.append(k)
  ret.sort()
  return ret

 #
 def signal_handler(self, sig, frame):
  from signal import SIGINT, SIGUSR1, SIGUSR2
  if   sig == SIGINT:
   self.close()
  elif sig == SIGUSR1:
   print("\n".join(self.module_reload()))
  elif sig == SIGUSR2:
   print(dumps({k:repr(v) for k,v in self.modules.items()},indent=4, sort_keys=True))


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
   mod = import_module("rims.rest.%s"%aTask['module'])
   func = getattr(mod,aTask['func'],None)
  except: pass
  else:
   if aSema:
    aSema.acquire()
   self._queue.put((func,'TASK',aSema,aTask['args'],{'output':aTask['output']}))

 def add_periodic(self, aTask, aFrequency):
  try:
   mod = import_module("rims.rest.%s"%aTask['module'])
   func = getattr(mod,aTask['func'],None)
  except: pass
  else:   self._scheduler.append(ScheduleWorker(aFrequency, func, aTask, self._queue, self._abort))

 def abort(self): self._abort.set()

 def join(self): self._queue.join()

 def done(self): return self._queue.empty()

 def queue_size(self):return self._queue.qsize()

 def pool_size(self): return self._thread_count

 def scheduler_size(self): return len(self._scheduler)

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
      log("%s - %s => %s"%(self.name,repr(func),dumps(result)), self._ctx.config['logs']['system'])
   except Exception as e:
    log("%s - ERROR => %s"%(self.name,str(e)), self._ctx.config['logs']['system'])
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
  self._headers.update({'X-Method':self.command,'Server':'Engine %s.%s'%(__version__,__minor__),'Date':self.date_time_string()})
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
  if path in ['api','debug','external']:
   self.api(path,query)
  elif path in ['infra','images','files']:
   self.files(path,query)
  elif path == 'site' and len(query) > 0:
   self.site(query)
  elif path == 'auth':
   self.auth()
  elif path == 'system':
   self.system(query)
  else:
   self._headers.update({'X-Process':'no route','Location':'%s/site/system_portal'%(self._ctx.nodes[self._ctx.node]['url']),'X-Code':301})

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
    with open(self._ctx.config['logs']['rest'], 'a') as f:
     f.write(str("%s: %s '%s' @%s(%s)\n"%(strftime('%Y-%m-%d %H:%M:%S', localtime()), api, dumps(args) if api != "system_task_worker" else "N/A", self._ctx.node, get.strip())))
   except: pass
  try:
   if self._headers['X-Node'] == self._ctx.node:
    module = import_module("rims.rest.%s"%mod) if not path == 'external' else self._ctx.modules.get(mod)
    self._body = dumps(getattr(module,fun,None)(args,self._ctx)).encode('utf-8')
   else:
    req  = Request("%s/%s/%s"%(self._ctx.nodes[self._headers['X-Node']]['url'],path,query), headers = { 'Content-Type': 'application/json','Accept':'application/json' }, data = dumps(args).encode('utf-8'))
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
   module = import_module("rims.site.%s"%mod)
   getattr(module,fun,None)(stream)
  except Exception as e:
   stream.wr("<DETAILS CLASS='web'><SUMMARY CLASS='red'>ERROR</SUMMARY>API:&nbsp; rims.site.%s<BR>"%(api))
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
  self._headers['X-Process'] = 'files'
  if query.endswith(".js"):
   self._headers['Content-type']='application/javascript; charset=utf-8'
  elif query.endswith(".css"):
   self._headers['Content-type']='text/css; charset=utf-8'
  try:
   from os import walk, path as ospath
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
  """ Authenticate using node function instead of API """
  self._headers.update({'Content-type':'application/json; charset=utf-8','X-Process':'auth','X-Code':401})
  try:
   length = int(self.headers['Content-Length'])
   args   = loads(self.rfile.read(length).decode()) if length > 0 else {}
   username, password = args['username'], args['password']
  except Exception as e:  output['error'] = {'argument':str(e)}
  else:
   if self._ctx.node == 'master':
    output = {}
    from rims.core.genlib import random_string
    from hashlib import md5
    from datetime import datetime,timedelta
    try:
     hash = md5()
     hash.update(password.encode('utf-8'))
     passcode = hash.hexdigest()
    except Exception as e: output['error'] = {'hash':str(e)}
    else:
     with self._ctx.db as db:
      if (db.do("SELECT id FROM users WHERE alias = '%s' and password = '%s'"%(username,passcode)) == 1):
       output['token']   = random_string(16)
       output['id']      = db.get_val('id')
       output['expires'] = (datetime.utcnow() + timedelta(days=30)).strftime("%a, %d %b %Y %H:%M:%S GMT")
       self._headers['X-Code'] = 200
      else:
       output['error'] = {'authentication':'username and password combination not found','username':username,'passcode':passcode}
   else:
    req  = Request("%s/auth"%(self._ctx.config['master']), headers = { 'Content-Type': 'application/json','Accept':'application/json'}, data = dumps(args).encode('utf-8'))
    try: sock = urlopen(req, timeout = 300)
    except HTTPError as h:
     try:
      data   = h.read()
      output = {'error':loads(data.decode())['error']}
     except: output = {'error':{'master':str(h)}}
     else:   output['code'] = h.code
    except Exception as e:
     output = {'error':{'master':str(e)}}
    else:
     try:      output = loads(sock.read().decode())
     except:   output = {'error':{'remote response decode error'}}
     else:     self._headers['X-Code'] = 200
     finally:  sock.close()
  output['node'] = self._ctx.node
  self._body = dumps(output).encode('utf-8')

 #
 #
 def system(self,query):
  """ /system/<op>/<node> """
  self._headers.update({'Content-type':'application/json; charset=utf-8','X-Process':'system'})
  op,_,node = query.partition('/')
  if self._ctx.node == 'master' and (op == 'info' or (op == 'sync' and node != 'master')):
   settings = self._ctx.system_info(node)
   if op == 'info':
    output = settings
   else:
    req  = Request("%s/system/update"%(self._ctx.nodes[node]['url']), headers = { 'Content-Type': 'application/json','Accept':'application/json'}, data = dumps(settings).encode('utf-8'))
    try: sock = urlopen(req, timeout = 300)
    except Exception as e:
     self._headers.update({ 'X-Exception':type(e).__name__, 'X-Code':590, 'X-Info':str(e)})
     output = {'node':node,'result':'SYNC_NOT_OK'}
    else:
     output = {'node':node,'result':'SYNC_OK'}
  elif op == 'show':
   output = {'settings':self._ctx.settings,'nodes':self._ctx.nodes,'servers':self._ctx.servers,'config':self._ctx.config}
  elif op == 'update':
   length = int(self.headers['Content-Length'])
   args = loads(self.rfile.read(length).decode()) if length > 0 else {}
   self._ctx.settings.clear()
   self._ctx.settings.update(loads(args.get('settings',{})))
   output = {'node':self._ctx.node,'result':'UPDATE_OK'}
  elif op == 'reload':
   res = self._ctx.module_reload()
   output = {'modules':res}
  elif op == 'register':
   length = int(self.headers['Content-Length'])
   args = loads(self.rfile.read(length).decode()) if length > 0 else {}
   params = {'node':node,'url':"http://%s:%s"%(self.client_address[0],args['port']),'system':args.get('system','0')}
   with self._ctx.db as db:
    update = db.insert_dict('nodes',params,"ON DUPLICATE KEY UPDATE system = %(system)s, url = '%(url)s'"%params)
   output = {'update':update,'success':True}
  else:
   output = {'result':'NOT_OK','info':'system/<register|show|info|sync|reload>/<node> where show and reload runs on any node'}
  self._body = dumps(output).encode('utf-8')

########################################### Web stream ########################################
#

class Stream(object):

 def __init__(self,aHandler, aGet):
  self._form = {}
  self._node = aHandler._ctx.node
  self._body = []
  self._cookies   = {}
  self._node_url  = aHandler._ctx.nodes[self._node]['url']
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

 def url(self):
  return self._node_url

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
  return self._rest_call("%s/api/%s"%(self._node_url,aAPI), aArgs, aTimeout = 60)['data']

 def rest_full(self, aURL, aArgs = None, aMethod = None, aHeader = None, aTimeout = 20):
  return self._rest_call(aURL, aArgs, aMethod, aHeader, True, aTimeout)

 def put_html(self, aTitle = None, aIcon = 'rims.ico'):
  self._body.append("<!DOCTYPE html><HEAD><META CHARSET='UTF-8'><LINK REL='stylesheet' TYPE='text/css' HREF='../infra/4.21.0.vis.min.css' /><LINK REL='stylesheet' TYPE='text/css' HREF='../infra/system.css'>")
  if aTitle:
   self._body.append("<TITLE>" + aTitle + "</TITLE>")
  self._body.append("<LINK REL='shortcut icon' TYPE='image/png' HREF='../images/%s'/>"%(aIcon))
  self._body.append("<SCRIPT SRC='../infra/3.1.1.jquery.min.js'></SCRIPT><SCRIPT SRC='../infra/4.21.0.vis.min.js'></SCRIPT><SCRIPT SRC='../infra/system.js'></SCRIPT>")
  self._body.append("<SCRIPT>$(function() { $(document.body).on('click','.z-op',btn ) .on('focusin focusout','input, select',focus ) .on('input','.slider',slide_monitor); });</SCRIPT>")
  self._body.append("</HEAD>")
