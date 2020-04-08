"""System engine"""
__author__ = "Zacharias El Banna"
__version__ = "6.0"
__build__ = 300
__all__ = ['Context','WorkerPool']

from os import path as ospath, getpid, walk
from sys import stdout
from json import loads, load, dumps
from importlib import import_module, reload as reload_module
from threading import Thread, Event, BoundedSemaphore, enumerate as thread_enumerate
from time import localtime, strftime, time, sleep
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote, parse_qs
from functools import partial
from base64 import b64encode, b64decode
from datetime import datetime,timedelta, timezone
from crypt import crypt
from rims.core.common import DB, rest_call

########################################### Context ########################################
#
# Main state object, contains config, workers, modules and calls etc..
#
# TODO EXTRA: make multiprocessing - preforking - and multithreaded
#
# - http://stupidpythonideas.blogspot.com/2014/09/sockets-and-multiprocessing.html
# - https://stackoverflow.com/questions/1293652/accept-with-sockets-shared-between-multiple-processes-based-on-apache-prefork
# - CTX data is unique/non-mutable and could be parallelized
#

class Context(object):

 def __init__(self,aConfig):
  """ Context init - create the infrastructure but populate later
  - Set node ID
  - Prepare database and workers
  - Load config
  - initiate the 'kill' switch
  - create datastore (i.e. dict) for nodes, services and external modules
  """
  if isinstance(aConfig, dict):
   self.config = aConfig
  else:
   with open(aConfig,'r') as config_file:
    self.config = load(config_file)
    self.config['config_file'] = aConfig
  self.config['salt'] = self.config.get('salt','WBEUAHfO')
  self.config['mode'] = self.config.get('mode','api')
  self.config['workers']= self.config.get('workers',20)
  self.node     = self.config['id']
  self.db       = DB(self.config['database']['name'],self.config['database']['host'],self.config['database']['username'],self.config['database']['password']) if self.config.get('database') else None
  self.workers  = WorkerPool(self.config['workers'],self)
  self.path     = ospath.abspath(ospath.join(ospath.dirname(__file__), '..'))
  self.tokens   = {}
  self.nodes    = {}
  self.external = {}
  self.services = {}
  self.config['logging'] = self.config.get('logging',{})
  self.config['logging']['rest']   = self.config['logging'].get('rest',{'enabled':False,'file':None})
  self.config['logging']['system'] = self.config['logging'].get('system',{'enabled':False,'file':None})
  try:
   with open(self.config['site_file'],'r') as sfile:
    self.site = load(sfile)
  except:
   self.log("Site file could not be loaded/found: %s"%self.config.get('site_file','N/A'))
   self.site = {}
  for type in ['menuitem','tool']:
   for k,item in self.site.get(type,{}).items():
    for tp in ['module','frame','tab']:
     if tp in item:
      item['type'] = tp
      break
  self._kill    = Event()
  self._analytics= {'files':{},'modules':{}}
  self.rest_call = rest_call

 def __str__(self):
  return "Context(node=%s)"%(self.node)

 #
 def clone(self):
  """ Clone itself and non thread-safe components, avoid using copy and having to copy everything manually... """
  from copy import copy
  ctx_new = copy(self)
  ctx_new.db = DB(self.config['database']['name'],self.config['database']['host'],self.config['database']['username'],self.config['database']['password']) if self.config.get('database') else None
  return ctx_new

 #
 def wait(self):
  self._kill.wait()

 #
 def system_info(self,aNode):
  """ Function retrieves all central info for a certain node, or itself if node is given"""
  if len(aNode) == 0 or aNode is None:
   info = {'nodes':self.nodes,'services':self.services,'config':self.config,'tasks':self.workers.scheduler_tasks(),'site':(len(self.site) > 0),'version':__version__,'build':__build__}
  elif self.config.get('database'):
   info = {'tokens':{}}
   with self.db as db:
    db.do("SELECT id, node, url FROM nodes")
    info['nodes']   = {x['node']:{'id':x['id'],'url':x['url']} for x in db.get_rows()}
    db.do("SELECT servers.id, node, st.service, st.type FROM servers LEFT JOIN service_types AS st ON servers.type_id = st.id")
    info['services'] = {x['id']:{'node':x['node'],'service':x['service'],'type':x['type']} for x in db.get_rows()}
    db.do("SELECT tasks.id, module, function, args, frequency, output FROM tasks LEFT JOIN nodes ON nodes.id = tasks.node_id WHERE node = '%s'"%aNode)
    info['tasks']   = db.get_rows()
    for task in info['tasks']:
     task['output'] = (task['output']== 'true')
    db.do("DELETE FROM user_tokens WHERE created + INTERVAL 5 DAY < NOW()")
    db.do("SELECT user_id, token, created + INTERVAL 5 DAY as expires FROM user_tokens ORDER BY created DESC")
    info['tokens'] = {x['token']:(x['user_id'],x['expires'].strftime("%a, %d %b %Y %H:%M:%S GMT")) for x in db.get_rows()}
   info['version'] = __version__
   info['build'] = __build__
  else:
   info = self.rest_call("%s/system/environment/%s/%s"%(self.config['master'],aNode,__build__), aDataOnly = True)
  return info

 #
 def load_system(self):
  """ Load info from DB or retrieve from master node. Add tasks to queue, return true if system loaded successfully"""
  try:
   system = self.system_info(self.node)
  except Exception as e:
   print(str(e))
   return False
  else:
   self.log("______ Loading system - version: %s mode: %s ______"%(__build__,self.config['mode']))
   self.nodes.update(system['nodes'])
   self.services.update(system['services'])
   self.tokens.update(system['tokens'])
   for task in system['tasks']:
    try:    freq = int(task.pop('frequency'))
    except: freq = 0
    self.log("Adding task: %(module)s/%(function)s"%task)
    self.workers.add_task(task['module'],task['function'],freq,args = loads(task['args']), output = (task['output'] in ['true',True]))
   if __build__ != system['build']:
    self.log("Build mismatch between master and node: %s != %s"%(__build__,system['build']))
   return True

 #
 def start(self):
  """ Start "moving" parts of context, set up socket and start processing incoming requests and scheduled tasks """
  from sys import setcheckinterval
  from signal import signal, SIGINT, SIGUSR1, SIGUSR2
  from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
  try:
   addr = ("", int(self.config['port']))
   sock = socket(AF_INET, SOCK_STREAM)
   sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
   sock.bind(addr)
   sock.listen(5)
   self.workers.start(addr,sock)
   for sig in [SIGINT, SIGUSR1, SIGUSR2]:
    signal(sig, self.signal_handler)
   setcheckinterval(200)
  except Exception as e:
   print(str(e))
   return False
  else:
   self.log("______ REST server workers started ______")
   return True

 #
 def close(self):
  self.workers.close()
  self._kill.set()

 #
 def signal_handler(self, sig, frame):
  """ Signal handler instantiate OS signalling mechanisms to override standard behavior
   - SIGINT: close system
   - SIGUSR1: reload system modules and cache files
   - SIGUSR2: report system state through stdout print
  """
  from signal import SIGINT, SIGUSR1, SIGUSR2
  if   sig == SIGINT:
   self.close()
  elif sig == SIGUSR1:
   print("\n".join(self.module_reload()))
  elif sig == SIGUSR2:
   data = self.report()
   data.update(self.config)
   data['tokens'] = {k:(v[0],v[1]) for k,v in self.tokens.items()}
   data['site'] = self.site
   print("System Info:\n_____________________________\n%s\n_____________________________"%(dumps(data,indent=2, sort_keys=True)))

 #
 def debugging(self):
  return (self.config['mode'] == 'debug')

 ################################## Service Functions #################################
 #
 def node_function(self, aNode, aModule, aFunction, **kwargs):
  """ Node function freezes a REST call or a function with enough info so that they can be used multiple times AND interchangably """
  if self.node != aNode:
   kwargs['aDataOnly'] = True
   try: ret = partial(self.rest_call,"%s/api/%s/%s"%(self.nodes[aNode]['url'],aModule,aFunction), **kwargs)
   except Exception as e:
    self.log("Node Function REST failure: %s/%s@%s (%s) => %s"%(aModule,aFunction,aNode,dumps(kwargs),str(e)))
    ret = {'status':'NOT_OK','info':'NODE_FUNCTION_FAILURE: %s'%str(e)}
  else:
   module = import_module("rims.rest.%s"%aModule)
   fun = getattr(module,aFunction,lambda aCTX,aArgs: None)
   ret = partial(fun,self)
  return ret

 #
 def module_register(self, aName):
  """ Register "external" modules - for dynamic modules """
  ret = {}
  try:   module = import_module(aName)
  except Exception as e:
   ret['status'] = 'NOT_OK'
   ret['info'] = str(e)
  else:
   ret['status'] = 'OK'
   self.external[aName] = module
   ret['import'] = repr(module)
  return ret

 #
 def module_reload(self):
  """ Reload modules and return which ones were reloaded """
  from sys import modules as sys_modules
  from types import ModuleType
  modules = {x:sys_modules[x] for x in sys_modules.keys() if x.startswith('rims.')}
  modules.update(self.external)
  ret = []
  for k,v in modules.items():
   if isinstance(v,ModuleType):
    try: reload_module(v)
    except: pass
    else:   ret.append(k)
  ret.sort()
  return ret

 #
 def analytics(self, aType, aGroup, aItem):
  """ Function provides basic usage analytics """
  tmp = self._analytics[aType].get(aGroup,{})
  tmp[aItem] = tmp.get(aItem,0) + 1
  self._analytics[aType][aGroup] = tmp

 #
 # @debug_decorator('log')
 def log(self,aMsg):
  syslog = self.config['logging']['system']
  if syslog['enabled']:
   with open(syslog['file'], 'a') as f:
    f.write(str("%s: %s\n"%(strftime('%Y-%m-%d %H:%M:%S', localtime()), aMsg)))

 #
 def report(self):
  from sys import version, modules as sys_modules, path as syspath
  from types import ModuleType
  node_url = self.nodes[self.node]['url']
  db_counter = {}
  for t in thread_enumerate():
   try:
    for k,v in t._ctx.db.count.items():
     db_counter[k] = db_counter.get(k,0) + v
   except:pass
  output = {
  'Node URL':node_url,
  'Package path':self.path,
  'Python version':version.replace('\n',''),
  'Workers pool':self.workers.alive(),
  'Workers idle':self.workers.idles(),
  'Workers queue':self.workers.queue_size(),
  'Servers':self.workers.servers(),
  'Database':', '.join("%s:%s"%(k.lower(),v) for k,v in db_counter.items()),
  # 'OS path':', ' .join(syspath),
  'OS pid':getpid()}
  if self.config.get('database'):
   with self.db as db:
    oids = {}
    for type in ['devices','device_types']:
     db.do("SELECT DISTINCT oid FROM %s"%type)
     oids[type] = [x['oid'] for x in db.get_rows()]
   output['Unhandled detected OIDs']= ",".join(str(x) for x in oids['devices'] if x not in oids['device_types'])
   output.update({'Mounted directory: %s'%k:"%s => %s/files/%s/"%(v,node_url,k) for k,v in self.config.get('files',{}).items()})
   output.update({'Modules (%03d)'%i:x for i,x in enumerate(sys_modules.keys()) if x.startswith('rims')})
  for type in ['modules','files']:
   for group,item in self._analytics[type].items():
    for i,c in item.items():
     output['Access: %s/%s'%(group,i)] = c
  return output

########################################## WorkerPool ########################################
#
#
class WorkerPool(object):

 ###################################### Workers ########################################
 #

 class ScheduleWorker(Thread):
  # Class that provides a sleep-then-repeat function

  def __init__(self, aFrequency, aFunc, aName, aOutput, aArgs, aQueue, aAbort):
   Thread.__init__(self)
   self._freq  = aFrequency
   self._queue = aQueue
   self._func  = aFunc
   self.name   = aName
   self._output= aOutput
   self._args  = aArgs
   self._abort = aAbort
   self.daemon = True
   self.start()

  def run(self):
   self._abort.wait(self._freq - int(time())%self._freq)
   while not self._abort.is_set():
    self._queue.put((self._func,'TASK',None,self._output,self._args,None))
    self._abort.wait(self._freq)
   return False

 #
 #
 class QueueWorker(Thread):

  def __init__(self, aNumber, aAbort, aQueue, aContext):
   Thread.__init__(self)
   self._n      = aNumber
   self.name    = "QueueWorker(%02d)"%aNumber
   self._abort  = aAbort
   self._idle   = Event()
   self._queue  = aQueue
   self._ctx    = aContext.clone()
   self.daemon  = True
   self.start()

  def run(self):
   while not self._abort.is_set():
    try:
     self._idle.set()
     (func, rest, sema, output, args, kwargs) = self._queue.get(True)
     self._idle.clear()
     result = func(*args,**kwargs) if not rest else func(self._ctx, args)
     if output:
      self._ctx.log("%s - %s => %s"%(self.name,repr(func),dumps(result)))
    except Exception as e:
     self._ctx.log("%s - ERROR: %s => %s"%(self.name,repr(func),str(e)))
     if self._ctx.config['mode'] == 'debug':
      from traceback import format_exc
      for n,v in enumerate(format_exc().split('\n')):
       self._ctx.log("%s - DEBUG-%02d => %s"%(self.name,n,v))
    finally:
     if sema:
      sema.release()
     self._queue.task_done()
   return False

 #
 #
 class ServerWorker(Thread):

  def __init__(self, aNumber, aAddress, aSocket, aContext):
   Thread.__init__(self)
   self.name    = "ServerWorker(%02d)"%aNumber
   self.daemon  = True
   httpd        = HTTPServer(aAddress, SessionHandler, False)
   self._httpd  = httpd
   httpd.socket = aSocket
   httpd._ctx = self._ctx = aContext.clone()
   httpd.server_bind = httpd.server_close = lambda self: None
   self.start()

  def run(self):
   try: self._httpd.serve_forever()
   except: pass

  def shutdown(self):
   self._httpd.shutdown()

 #
 #
 def __init__(self, aWorkers, aContext):
  from queue import Queue
  self._queue     = Queue(0)
  self._count     = aWorkers
  self._ctx       = aContext
  self._abort     = Event()
  self._sock      = None
  self._idles     = []
  self._workers   = []
  self._servers   = []
  self._scheduler = []

 def __str__(self):
  return "WorkerPool(count = %s, queue = %s, schedulers = %s, alive = %s)"%(self._count,self._queue.qsize(),len(self._scheduler),self.alive())

 def start(self, aAddr, aSock):
  self._abort.clear()
  self._sock    = aSock
  self._servers = [self.ServerWorker(n,aAddr,aSock,self._ctx) for n in range(4)]
  self._workers = [self.QueueWorker(n, self._abort, self._queue, self._ctx) for n in range(self._count)]
  self._idles   = [w._idle for w in self._workers]

 def close(self):
  """ Abort set abort state and inject dummy tasks to kill off workers. There might be running tasks so don't add more than enough """
  def dummy(): pass
  self._abort.set()
  try: self._sock.close()
  except: pass
  finally: self._sock = None
  active = self.alive()
  while active > 0:
   for x in range(0,active - self._queue.qsize()):
    self._queue.put((dummy,False,None,False,[],{}))
   while not self._queue.empty() and self.alive() > 0:
    sleep(0.1)
    self._workers = [x for x in self._workers if x.is_alive()]
   active = self.alive()

 def alive(self):
  return len([x for x in self._workers if x.is_alive()])

 def idles(self):
  return len([x for x in self._idles if x.is_set()])

 def servers(self):
  return len([x for x in self._servers if x.is_alive()])

 def queue_size(self):
  return self._queue.qsize()

 def scheduler_size(self):
  return len([x for x in self._scheduler if x.is_alive()])

 def scheduler_tasks(self):
  return [(x.name,x._freq) for x in self._scheduler]

 def semaphore(self,aSize):
  return BoundedSemaphore(aSize)

 def block(self,aSema,aSize):
  for i in range(aSize):
   aSema.acquire()

 def block_map(self, aFunction, aList):
  """ Apply function on list elements and have at most 20 concurrent workers """
  nworkers = max(20,int(self._ctx.config['workers']) - 5)
  sema = self.semaphore(nworkers)
  for elem in aList:
   self.add_semaphore(aFunction, sema, elem)
  self.block(sema,nworkers)

 ##################### FUNCTIONs ########################
 #
 def add_function(self, aFunction, *args, **kwargs):
  self._queue.put((aFunction,False,None,False,args,kwargs))

 def add_semaphore(self, aFunction, aSema, *args, **kwargs):
  aSema.acquire()
  self._queue.put((aFunction,False,aSema,False,args,kwargs))

 ####################### TASKs ###########################
 #
 def add_task(self, aModule, aFunction, aFrequency = 0, **kwargs):
  try:
   mod = import_module("rims.rest.%s"%aModule)
   func = getattr(mod, aFunction, None)
  except: self._ctx.log("WorkerPool ERROR: adding task failed (%s/%s)"%(aModule,aFunction))
  else:
   if aFrequency > 0:
    self._scheduler.append(self.ScheduleWorker(aFrequency, func, "%s/%s"%(aModule,aFunction), kwargs.get('output',False), kwargs.get('args',{}), self._queue, self._abort))
   else:
    self._queue.put((func,True, None, kwargs.get('output',False), kwargs.get('args',{}), None))

###################################### Session Handler ######################################
#
class SessionHandler(BaseHTTPRequestHandler):

 def __init__(self, *args, **kwargs):
  self._headers = {}
  self._body    = b'null'
  self._ctx     = args[2]._ctx
  BaseHTTPRequestHandler.__init__(self,*args, **kwargs)

 def header(self):
  # Sends X-Code as response
  self._headers.update({'X-Method':self.command,'X-Powered-By':'RIMS Engine %s.%s'%(__version__,__build__),'Date':self.date_time_string()})
  code = self._headers.pop('X-Code',200)
  self.wfile.write(('HTTP/1.1 %s %s\r\n'%(code,self.responses.get(code,('Other','Server specialized return code'))[0])).encode('utf-8'))
  self._headers.update({'Content-Length':len(self._body),'Connection':'close'})
  for k,v in self._headers.items():
   try: self.send_header(k,v)
   except: self.send_header('X-Header-Error',k)
  self.end_headers()

 def do_GET(self):
  #print('GET: ' + self.path)
  """ Route request to the right function /<path>/mod_fun?get """
  path,_,query = self.path[1:].partition('/')
  if path in ['infra','images','files','static']:
   # Use caching here :-)
   if self.headers.get('If-None-Match') and self.headers['If-None-Match'][3:-1] == str(__build__):
    self._headers['X-Code'] = 304
   else:
    self.files(path,query)
  elif len(path) == 0:
   self._headers.update({'X-Process':'no route','Location':'index.html','X-Code':301})
  else:
   self.files('',path)
  self.header()
  try: self.wfile.write(self._body)
  except Exception as e:
   print("do_GET: Error writing above body => %s"%str(e))

 def do_POST(self):
  # print('POST:' + self.path)
  """ Route request to the right function /<path>/mod_fun?get"""
  path,_,query = self.path[1:].partition('/')
  if path in ['api','external']:
   self.api(path,query)
  elif path == 'front':
   self.front()
  elif path == 'auth':
   self.auth()
  elif path == 'system':
   self.system(query)
  else:
   self._headers.update({'X-Process':'no route','X-Code':404})
  self.header()
  self.wfile.write(self._body)

 def do_OPTIONS(self):
  self._headers.update({'Access-Control-Allow-Headers':'X-Token,Content-Type','Access-Control-Allow-Origin':'*'})
  self.header()
  self.wfile.write(self._body)

 #
 #
 def api(self,path,query):
  """ API serves the REST functions x.y.z.a:<port>/api|external/module/function
   - extra arguments can be sent as GET or using headers (using X-prefix in the latter case): node
   - Should get a cookie
  """
  extras = {}
  (api,_,get) = query.partition('?')
  (mod,_,fun) = api.partition('/')
  self._ctx.analytics('modules',mod,fun)
  for part in get.split("&"):
   (k,_,v) = part.partition('=')
   extras[k] = v
  self._headers.update({'X-Module':mod, 'X-Function': fun,'Content-Type':"application/json; charset=utf-8",'Access-Control-Allow-Origin':"*",'X-Process':'API','X-Route':self.headers.get('X-Route',extras.get('node',self._ctx.node if not mod == 'master' else 'master'))})
  try:
   length = int(self.headers.get('Content-Length',0))
   if length > 0:
    raw = self.rfile.read(length).decode()
    header,_,_ = self.headers['Content-Type'].partition(';')
    if   header == 'application/json': args = loads(raw)
    elif header == 'application/x-www-form-urlencoded':   args = { k: l[0] for k,l in parse_qs(raw, keep_blank_values=1).items() }
    else: args = {}
   else:  args = {}
  except: args = {}
  if self._ctx.config['logging']['rest']['enabled'] and self.headers.get('X-Log','true') == 'true':
   logstring = str("%s: %s '%s' @%s(%s)\n"%(strftime('%Y-%m-%d %H:%M:%S', localtime()), api, dumps(args) if api != "system/worker" else "N/A", self._ctx.node, get.strip()))
   if self._ctx.config['logging']['rest']['enabled'] == 'debug':
    stdout.write(logstring)
   else:
    with open(self._ctx.config['logging']['rest']['file'], 'a') as f:
     f.write(logstring)
  try:
   if self._headers['X-Route'] == self._ctx.node:
    module = import_module("rims.rest.%s"%mod) if not path == 'external' else self._ctx.external.get(mod)
    self._body = dumps(getattr(module,fun, lambda x,y: None)(self._ctx, args)).encode('utf-8')
   else:
    self._body = self._ctx.rest_call("%s/%s/%s"%(self._ctx.nodes[self._headers['X-Route']]['url'],path,query), aArgs = args, aDecode = False, aDataOnly = True)
  except Exception as e:
   if not (isinstance(e.args[0],dict) and e.args[0].get('code')):
    error = {'X-Args':args, 'X-Exception':type(e).__name__, 'X-Code':600, 'X-Info':','.join(map(str,e.args))}
   else:
    error = {'X-Args':args, 'X-Exception':e.args[0].get('exception'), 'X-Code':e.args[0]['code'], 'X-Info':e.args[0].get('info')}
   self._headers.update(error)
   if self._ctx.config['mode'] == 'debug':
    from traceback import format_exc
    for n,v in enumerate(format_exc().split('\n')):
     self._headers["X-Debug-%02d"%n] = v

 #
 #
 def files(self,path,query):
  """ Serve "common" system files and also route 'files' """
  query = unquote(query)
  self._ctx.analytics('files', path, query)
  self._headers.update({'X-Process':'files','Cache-Control':'public, max-age=0','ETag':'W/"%s"'%__build__})
  _,_,ftype = query.rpartition('.')
  if ftype == 'js':
   self._headers['Content-type']='application/javascript; charset=utf-8'
  elif ftype == 'css':
   self._headers['Content-type']='text/css; charset=utf-8'
  elif ftype == 'html':
   self._headers['Content-type']='text/html; charset=utf-8'
  try:
   if not path == 'files':
    fullpath = ospath.join(self._ctx.path,'build',path,query)
   else:
    param,_,file = query.partition('/')
    fullpath = ospath.join(self._ctx.config['files'][param],file)
   if not fullpath.endswith("/"):
    with open(fullpath, 'rb') as file:
     self._body = file.read()
   else:
    self._headers['Content-type']='text/html; charset=utf-8'
    _, _, filelist = next(walk(fullpath), (None, None, []))
    self._body = ("<BR>".join("<A HREF='{0}'>{0}</A>".format(file) for file in filelist)).encode('utf-8')
  except Exception as e:
   self._headers.update({'X-Exception':str(e),'X-Query':query,'X-Path':path,'Content-type':'text/html; charset=utf-8','X-Code':404})
   self._body = b''

 #
 #
 def front(self):
  self._headers.update({'Content-type':'application/json; charset=utf-8','X-Process':'front','Access-Control-Allow-Origin':"*"})
  output = {'message':"Welcome to the Management Portal",'title':'Portal'}
  output.update(self._ctx.site.get('portal'))
  self._body = dumps(output).encode('utf-8')

 #
 #
 def auth(self):
  """ Authenticate using node function instead of API """
  self._headers.update({'Content-type':'application/json; charset=utf-8','X-Process':'auth','X-Code':401,'Access-Control-Allow-Origin':"*"})
  output = {'status':'NOT_OK'}
  try:
   length = int(self.headers.get('Content-Length',0))
   args   = loads(self.rfile.read(length).decode()) if length > 0 else {}
   username, password = args['username'], args['password']
  # except: output['info'] = "Provide username and password arguments"
  except Exception as e:
   output['info'] = {'argument':str(e)}
  else:
   if self._ctx.node == 'master':
    from rims.core.genlib import random_string
    passcode = crypt(password, "$1$%s$"%self._ctx.config['salt']).split('$')[3]
    with self._ctx.db as db:
     if (db.do("SELECT id, theme FROM users WHERE alias = '%s' and password = '%s'"%(username,passcode)) == 1):
      output.update(db.get_row())
      output['token']   = random_string(16)
      db.do("INSERT INTO user_tokens (user_id,token,source_ip,source_port) VALUES(%s,'%s',INET_ATON('%s'),%s)"%(output['id'],output['token'],self.client_address[0],self.client_address[1]))
      expires = datetime.now(timezone.utc) + timedelta(days=5)
      output['expires'] = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
      self._ctx.tokens[output['token']] = (output['id'],expires)
      self._headers['X-Code'] = 200
      output['status'] = 'OK'
     else:
      output['info'] = {'authentication':'username and password combination not found','username':username,'passcode':passcode}
   else:
    try:
     output = self._ctx.rest_call("%s/auth"%(self._ctx.config['master']), aArgs = args, aDataOnly = True)
     self._headers['X-Code'] = 200
     output['status'] = 'OK'
    except Exception as e:
     output = {'info':e.args[0]}
     self._headers['X-Code'] = e.args[0]['code']
  output['node'] = self._ctx.node
  self._body = dumps(output).encode('utf-8')

 #
 #
 def system(self,query):
  """ /system/<op>/<args> """
  self._headers.update({'Content-type':'application/json; charset=utf-8','X-Process':'system','Access-Control-Allow-Origin':'*'})
  op,_,arg = query.partition('/')
  if op == 'environment':
   env = arg.partition('/')
   if len(env[0]) > 0:
    self._ctx.log("Node '%s' connected, running version: %s"%(env[0],env[2]))
   output = self._ctx.system_info(env[0])
  elif op == 'reload':
   if (len(arg) > 0) and arg != self._ctx.node:
    try:
     output = self._ctx.rest_call(self._ctx.nodes[arg]['url'] + '/system/reload')
    except Exception as e:
     output = {'node':arg,'modules':[],'status':'NOT_OK','info':'Remote reload error: %s'%str(e)}
   else:
    output = {'node':self._ctx.node, 'modules':self._ctx.module_reload(),'status':'OK'}
  elif op == 'report':
   output = self._ctx.report()
  elif op == 'register':
   length = int(self.headers.get('Content-Length',0))
   args = loads(self.rfile.read(length).decode()) if length > 0 else {}
   params = {'node':arg,'url':"http://%s:%s"%(self.client_address[0],args['port']),'system':args.get('system','0')}
   output = {'status':'OK'}
   with self._ctx.db as db:
    output['update'] = db.insert_dict('nodes',params,"ON DUPLICATE KEY UPDATE system = %(system)s, url = '%(url)s'"%params)
   self._ctx.log("Registered node %s: update:%s"%(arg,output['update']))
  elif op == 'import':
   output = self._ctx.module_register(arg)
  elif op == 'shutdown':
   self._ctx.close()
   output = {'status':'OK','state':'shutdown in progress'}
  elif op == 'mode':
   self._ctx.config['mode'] = arg
   output = {'status':'OK','mode':arg}
  else:
   output = {'status':'NOT_OK','info':'system/<environment|reload|report|register|import|shutdown|mode>/<args: node|module_to_import> where import, environment without args and reload runs on any node'}
  self._body = dumps(output).encode('utf-8')
