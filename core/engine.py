"""System engine"""
__author__ = "Zacharias El Banna"
__version__ = "7.4"
__build__ = 395
__all__ = ['Context']

from copy import copy
from crypt import crypt
from datetime import datetime, timedelta, timezone
from functools import partial
from gc import collect as garbage_collect
from http.server import BaseHTTPRequestHandler, HTTPServer
from importlib import import_module, reload as reload_module
from json import loads, dumps
from os import path as ospath, getpid, walk, stat as osstat
from random import choice
from signal import signal, SIGINT, SIGUSR1, SIGUSR2, SIGTRAP
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from ssl import SSLContext, PROTOCOL_SSLv23
from string import ascii_uppercase, digits
from sys import stdout, modules as sys_modules, version, _current_frames as current_frames
from threading import Thread, Event, BoundedSemaphore, enumerate as thread_enumerate
from time import localtime, sleep, strftime, time
from traceback import format_exc, format_stack
from types import ModuleType
from urllib.parse import unquote, parse_qs
from queue import Queue
from ipaddress import ip_address
from rims.core.common import DB, rest_call, Scheduler, RestException

##################################################### Context #######################################################
#
# Main state object, contains config, workers, modules and calls etc..
#
class Context():

 def __init__(self,aConfig, aDebug = False):
  """ Context init - create the infrastructure but populate later
  - Consume config file
  - Set node ID
  - Prepare database and workers
  - initiate the 'kill' switch
  - create datastore (i.e. dict) for nodes, services
  """
  self.config = aConfig
  self._queue = Queue(0)
  self._abort = Event()
  self._kill  = Event()
  self._sock  = None
  self._ssock = None
  self._workers = []
  self._servers = []
  self._house_keeping = None
  self._scheduler = Scheduler(self._abort,self._queue)
  self._analytics = {'files':{},'modules':{}}
  self._start_time = int(time())

  database   = self.config.get('database')
  self.ip    = None
  self.node  = self.config['id']
  self.token = self.config.get('token')
  self.path  = ospath.abspath(ospath.join(ospath.dirname(__file__), '..'))
  self.site  = ospath.join(self.path,'site')
  self.debug = aDebug
  self.db    = DB(database['name'],database['host'],database['username'],database['password']) if database else None
  if self.config.get('services',{}).get('influxdb'):
   influxconfig = self.config['services']['influxdb']
   from influxdb_client import InfluxDBClient
   from influxdb_client.client.write_api import SYNCHRONOUS
   from influxdb_client.domain.write_precision import WritePrecision
   self.influxdb_client = InfluxDBClient(url=influxconfig['url'], token=influxconfig['token'], org=influxconfig['org']) if influxconfig.get('version') == 2 else InfluxDBClient(url=influxconfig['url'], token=f"{influxconfig['username']}:{influxconfig['password']}", org='-')
   self.influxdb_seconds = WritePrecision.S
   self.influxdb_synchronous = SYNCHRONOUS
  self.cache = {}
  self.nodes = {}
  self.tokens = {}
  self.services = {}
  self.rest_call = rest_call
  self.config['salt'] = self.config.get('salt','WBEUAHfO')
  self.config['workers'] = self.config.get('workers',20)
  self.config['logging'] = self.config.get('logging',{})
  self.config['logging']['rest']   = self.config['logging'].get('rest',{'enabled':False,'file':None})
  self.config['logging']['system'] = self.config['logging'].get('system',{'enabled':False,'file':None})
  if self.config.get('site'):
   for cls in ['menuitem','resource']:
    for v in self.config['site'].get(cls,{}).values():
     for tp in ['module','frame','tab']:
      if tp in v:
       v['type'] = tp
       break
  else:
   self.log('No site defined')

 #################### MAIN MACHINERY ##################
 #
 def clone(self):
  """ Clone itself and non thread-safe components, avoid using copy and having to copy everything manually... """
  ctx_new = copy(self)
  database = self.config.get('database')
  ctx_new.db = DB(database['name'],database['host'],database['username'],database['password']) if database else None
  if self.config.get('services',{}).get('influxdb'):
   influxconfig = self.config['services']['influxdb']
   from influxdb_client import InfluxDBClient
   from influxdb_client.client.write_api import SYNCHRONOUS
   self.influxdb_client = InfluxDBClient(url=influxconfig['url'], token=influxconfig['token'], org=influxconfig['org']) if influxconfig.get('version') == 2 else InfluxDBClient(url=influxconfig['url'], token=f"{influxconfig['username']}:{influxconfig['password']}", org='-')
  return ctx_new

 #
 def environment(self,aNode):
  """ Function retrieves all central environment for a certain node, or itself if node is given"""
  if not aNode:
   env = {'nodes':self.nodes,'services':self.services,'tasks':self.scheduler_status(),'site':(len(self.config['site']) > 0),'version':__version__,'build':__build__}
  elif self.config.get('database'):
   env = {'tokens':{}}
   with self.db as db:
    db.query("SELECT id, node, url FROM nodes")
    env['nodes']   = {x['node']:{'id':x['id'],'url':x['url']} for x in db.get_rows()}
    db.query("SELECT servers.id, node, st.service, st.type FROM servers LEFT JOIN service_types AS st ON servers.type_id = st.id")
    env['services'] = {x['id']:{'node':x['node'],'service':x['service'],'type':x['type']} for x in db.get_rows()}
    db.execute("DELETE FROM user_tokens WHERE created + INTERVAL 5 DAY < NOW()")
    db.query("SELECT users.id, ut.token, users.alias, ut.created + INTERVAL 5 DAY as expires, INET6_NTOA(ut.source_ip) AS ip, users.class FROM user_tokens AS ut LEFT JOIN users ON users.id = ut.user_id ORDER BY created DESC")
    env['tokens'] = {x['token']:{'id':x['id'], 'alias':x['alias'],'expires':x['expires'].replace(tzinfo=timezone.utc), 'ip':x['ip'], 'class':x['class']} for x in db.get_rows()}
   env['version'] = __version__
   env['build'] = __build__
  else:
   env = self.rest_call(f"{self.config['master']}/internal/system/environment", aHeader = {'X-Token':self.token}, aArgs = {'node':aNode,'build':__build__})
   env['nodes']['master']['url'] = self.config['master']
   for v in env['tokens'].values():
    v['expires'] = datetime.strptime(v['expires'],"%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc)
  try:
   self.ip = ip_address(env['nodes'][self.node]['url'].split(':')[1][2:].split('/')[0])
  except:
   self.ip = None
  return env

 #
 def load(self):
  """ Load environment from DB or retrieve from master node. Add tasks to queue, return true if system loaded successfully"""
  try:
   env = self.environment(self.node)
  except Exception as e:
   stdout.write(f"Load environment error: {e}\n")
   return False
  else:
   self.log("______ Loading system environment _____")
   self.log("Available signals: SIGINT, SIGUSR1, SIGUSR2, SIGTRAP")
   self.log(f"Version: {__build__}")
   self.log(f"Debug: {self.debug}")
   self.nodes.update(env['nodes'])
   self.services.update(env['services'])
   self.tokens.update(env.get('tokens',{}))
   for task in self.config.get('tasks',[]):
    self.log("Adding task: %(module)s/%(function)s"%task)
    self.schedule_api_task(task['module'],task['function'],int(task.get('frequency',0)), args = task.get('args',{}), output = task.get('output',False))

   if __build__ != env['build']:
    self.log(f"Build mismatch between master and node: {__build__} != {env['build']}")
   return True

 #
 def start(self):
  """ Start "moving" parts of context, workers and signal handlers to start processing incoming requests and scheduled tasks """

  def create_socket(port):
   """ Create a (secure) socket """
   addr = ('0.0.0.0', port)
   sock = socket(AF_INET, SOCK_STREAM, 0)
   sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
   sock.bind(addr)
   sock.listen(5)
   return (addr,sock)

  try:
   self._workers = [Worker(self, self._abort, n, self._queue) for n in range(self.config['workers'])]
   self._house_keeping = HouseKeeping(self, self._abort)
   self._abort.clear()
   self._scheduler.start()

   servers = 0
   if self.config.get('port'):
    self.log(f"Starting 'HTTP' server at: {self.config['port']}")
    addr,sock = create_socket(int(self.config['port']))
    self._sock = sock
    self._servers.extend(SocketServer(self, self._abort, n, addr, sock) for n in range(servers,servers+4))
    servers = 4
   if self.config.get('ssl'):
    ssl_config = self.config['ssl']
    self.log(f"Starting 'HTTPS' server at: {ssl_config['port']}")
    context = SSLContext(PROTOCOL_SSLv23)
    context.load_cert_chain(ssl_config['certfile'], keyfile=ssl_config['keyfile'], password=ssl_config.get('password'))
    addr,ssock = create_socket(int(ssl_config['port']))
    self._ssock = context.wrap_socket(ssock, server_side=True)
    self._servers.extend(SocketServer(self, self._abort, n, addr, self._ssock) for n in range(servers,servers+4))

   for sig in [SIGINT, SIGTRAP, SIGUSR1, SIGUSR2]:
    signal(sig, self.signal_handler)
  except Exception as e:
   stdout.write(f"Starting error - check IP and SSL settings: {e}\n")
   return False
  else:
   return True

 #
 def close(self):
  """ Abort set abort state and inject dummy tasks to kill off workers. There might be running tasks so don't add more than enough. Finally set kill to inform that we are done """
  def shutdown_dummy(n):
   return False
  self._abort.set()
  #
  # TODO:
  # 1) Empty queue
  # 2) Check if stuck workers and kill them if they been running for a long time
  # 3) Let short lived jobs complete, if there are stuck worker, just forget them as we can't kill threads
  #
  while self.workers_alive():
   # range is implicitly >= 0
   for x in range(self.workers_alive() - self._queue.qsize()):
    self._queue.put((shutdown_dummy,False,None,False,[x],{}))
   while self.workers_alive() and not self._queue.empty():
    sleep(0.2)
    self._workers = [x for x in self._workers if x.is_alive()]
  try:
   self._sock.close()
  except:
   pass
  finally:
   self._sock = None
  try:
   self._ssock.close()
  except:
   pass
  finally:
   self._ssock = None
  self._kill.set()

 #
 def wait(self):
  """ expose a 'wait' method for graceful shutdown """
  self._kill.wait()

 #
 def signal_handler(self, sig, frame):
  """ Signal handler instantiate OS signalling mechanisms to override standard behavior
   - SIGINT: close system
   - SIGTRAP: traceback of threads
   - SIGUSR1: reload system modules and cache files
   - SIGUSR2: report system state through stdout
  """
  if   sig == SIGINT:
   self.close()
  elif sig == SIGTRAP:
   for tid,stack in current_frames().items():
    stdout.write(f'Thread ID:{tid}\n')
    stdout.write(''.join(format_stack(stack)))
    stdout.write('\n')
  elif sig == SIGUSR1:
   stdout.write('\n'.join(self.module_reload()))
  elif sig == SIGUSR2:
   data = self.report()
   data.update(self.config)
   data['services'] = self.services
   data['tokens'] = {k:{'id':v['id'],'alias':v['alias'],'ip':v['ip'],'class':v['class'],'expires':v['expires'].strftime('%a, %d %b %Y %H:%M:%S %Z')} for k,v in self.tokens.items()}
   stdout.write(f"System Info:\n_____________________________\n{dumps(data,indent=2, sort_keys=True)}\n_____________________________\n")

 ######################## TOOLS #####################
 #
 def log(self,aMsg):
  """ Log a system message """
  syslog = self.config['logging']['system']
  if syslog['enabled']:
   logstring = f"{strftime('%Y-%m-%d %H:%M:%S', localtime())}: {aMsg}\n"
   if self.debug:
    stdout.write(logstring)
   else:
    with open(syslog['file'], 'a') as f:
     f.write(logstring)

 ################# API AND INTERNAL FUNCTIONS ##############
 #
 def node_function(self, aNode, aModule, aFunction, **kwargs):
  """
  Node function freezes a function (or convert to a REST call at node) with enough info so that the returned lambda can be used multiple times AND interchangably.
  For interchangably to work the argument to the function will have to be keyworded/**kwargs because if using REST then rest_call function picks everything from kwargs
  """
  if self.node != aNode:
   kwargs['aDataOnly'] = True
   kwargs['aHeader'] = kwargs.get('aHeader',{})
   kwargs['aHeader']['X-Token'] = self.token
   try:
    ret = partial(self.rest_call,f"{self.nodes[aNode]['url']}/internal/{aModule.replace('.','/')}/{aFunction}", **kwargs)
   except Exception as e:
    self.log(f"Node Function REST failure: {aModule}/{aFunction}@{aNode} ({dumps(kwargs)}) => {e}")
    ret = {'status':'NOT_OK','info':f"NODE_FUNCTION_FAILURE: {e}"}
  else:
   module = import_module(f"rims.api.{aModule}")
   fun = getattr(module,aFunction,lambda aCTX,aArgs: None)
   ret = partial(fun,self)
  return ret

 #
 @staticmethod
 def module_reload():
  """ Reload modules and return which ones were reloaded """
  modules = {x:sys_modules[x] for x in sys_modules if x.startswith('rims.')}
  ret = []
  for k,v in modules.items():
   if isinstance(v,ModuleType):
    try:
     reload_module(v)
    except:
     pass
    else:
     ret.append(k)
  ret.sort()
  return ret

 #
 def analytics(self, aType, aGroup, aItem):
  """ Function provides basic usage analytics """
  try:
   tmp = self._analytics[aType][aGroup]
  except:
   self._analytics[aType][aGroup] = tmp = {}
  finally:
   tmp[aItem] = tmp.get(aItem,0) + 1

 #
 def report(self):
  """ Create a report of system and activities """
  node_url = self.nodes[self.node]['url']
  db_counter = {}
  for t in thread_enumerate():
   try:
    for k,v in t.db_analytics():
     db_counter[k] = db_counter.get(k,0) + v
   except:
    pass
  output = {
   'Uptime': int(time()) - self._start_time,
   'Node URL':node_url,
   'Package path':self.path,
   'Python version':version.replace('\n',''),
   'Worker pool':self.workers_alive(),
   'Worker idle':self.workers_idle(),
   'Worker queue':self.queue_size(),
   'Servers':self.workers_servers(),
   'Active Tokens':len(self.tokens),
   'Database':', '.join(f"{k.lower()}:{v}" for k,v in db_counter.items()),
   'OS pid':getpid()}
  output.update(dict((w[0],f'{w[1]} / {w[2]}') for w in self.workers_active()))
  if self.config.get('database'):
   with self.db as db:
    oids = {}
    for tp in ['devices','device_types']:
     db.query(f"SELECT DISTINCT oid FROM {tp}")
     oids[tp] = [x['oid'] for x in db.get_rows()]
   output['Unhandled detected OIDs']= ",".join(str(x) for x in oids['devices'] if x not in oids['device_types'])
   output.update({f"Mounted directory: {k}":f"{v} => {node_url}/files/{k}/" for k,v in self.config.get('files',{}).items()})
   output.update({f"Modules ({i:03})":x for i,x in enumerate(sys_modules.keys()) if x.startswith('rims')})
  for tp in ['modules','files']:
   for group,item in self._analytics[tp].items():
    for i,c in item.items():
     output[f'Access: {group}/{i}'] = c
  return output

 ################# AUTHENTICATION ################
 #
 def auth_exec(self, aAlias, aIP, aOP):
  """ 'authenticate' or 'invalidate' alias and ip with external services, use 2 hours as a timeout and rely on house_keeping to update regularly """
  for infra in [{'service':v['service'],'node':v['node']} for v in self.services.values() if v['type'] == 'AUTHENTICATION']:
   res = self.node_function(infra['node'], f"services.{infra['service']}", aOP)(aArgs = {'alias':aAlias, 'ip': aIP, 'timeout':7200})
   self.log(f"Authentication service for '{aAlias}' ({aOP} {infra['service']}@{infra['node']}) => {res['status']} ({res.get('info','N/A')})")
  return True

 #################### QUEUE #####################
 #
 def queue_api(self, aFunction, aArgs, aSema = None, aOutput = False):
  """ Enqueue API function """
  if aSema:
   aSema.acquire()
  self._queue.put((aFunction, True, aSema, aOutput, aArgs, {}))

 def queue_function(self, aFunction, *args, **kwargs):
  """ Enqueue a function """
  self._queue.put((aFunction,False,None,False,args,kwargs))

 def queue_semaphore(self, aFunction, aSema, *args, **kwargs):
  """ Enqueue a function which require a semaphore """
  aSema.acquire()
  self._queue.put((aFunction,False,aSema,False,args,kwargs))

 def queue_block(self, aFunction, aList):
  """ Apply function on list elements and have at most 20 concurrent workers """
  nworkers = max(20,int(self.config['workers']) - 5)
  sema = BoundedSemaphore(value = nworkers)
  for elem in aList:
   self.queue_semaphore(aFunction, sema, elem)
  for _ in range(nworkers):
   sema.acquire()

 def queue_size(self):
  """ Return the current queue size """
  return self._queue.qsize()

 @staticmethod
 def semaphore(aSize):
  """ Generate a semaphor """
  return BoundedSemaphore(value = aSize)

 ################## STATUS TOOLS ################
 #
 def workers_active(self):
  now = int(time())
  return [(w.name, w.func, now - w.runtime(), w.ident) for w in self._workers if not w.is_idle()]

 def workers_alive(self):
  return len([w for w in self._workers if w.is_alive()])

 def workers_idle(self):
  return len([w for w in self._workers if w.is_idle()])

 def workers_servers(self):
  return len([s for s in self._servers if s.is_alive()])

 #################### SCHEDULING ################
 #
 def schedule_api(self, aFunction, aName, aDelay, aFrequency = 0, **kwargs):
  self._scheduler.add_delayed((aFunction, True, None, kwargs.get('output',False), kwargs.get('args',{}), None), aName, aDelay, aFrequency)

 def schedule_api_task(self, aModule, aFunction, aFrequency = 0, **kwargs):
  try:
   mod = import_module(f"rims.api.{aModule.replace('/','.')}")
   func = getattr(mod, aFunction, None)
  except:
   self.log(f"WorkerPool ERROR: adding task failed ({aModule}/{aFunction}")
   return False
  else:
   if aFrequency:
    self._scheduler.add_periodic((func, True, None, kwargs.get('output',False), kwargs.get('args',{}), None),f"{aModule}/{aFunction}",aFrequency)
   else:
    self._queue.put((func, True, None, kwargs.get('output',False), kwargs.get('args',{}), None))
   return True

 def schedule_api_periodic(self, aFunction, aName, aFrequency, **kwargs):
  self._scheduler.add_periodic((aFunction, True, None, kwargs.get('output',False), kwargs.get('args',{}), None), aName, aFrequency)

 def schedule_function(self, aFunction, aName, aDelay, aFrequency = 0, aPrio = 2, **kwargs):
  self._scheduler.add_delayed((aFunction, False, None, kwargs.pop('output',False), kwargs.pop('args',{}), kwargs), aName, aDelay, aFrequency, aPrio)

 def scheduler_status(self):
  return [(e[1]['name'],e[1]['frequency'],e[0]) for e in self._scheduler.events()]

#
#
################################################### Session Handler #####################################################
#
#
class SessionHandler(BaseHTTPRequestHandler):

 def __init__(self, *args, **kwargs):
  self._headers = {'X-Powered-By':f"RIMS Engine {__version__}.{__build__}",'Date':self.date_time_string()}
  self._body = b'null'
  self._ctx = args[2]._ctx
  BaseHTTPRequestHandler.__init__(self,*args, **kwargs)

 #
 @staticmethod
 def __read_generator(fd, size = 1024):
  while True:
   chunk = fd.read(size)
   if not chunk:
    break
   yield chunk

 #
 @staticmethod
 def __randomizer(aLength):
  return ''.join(choice(ascii_uppercase + digits) for _ in range(aLength))

 #
 def header(self,code,text,size):
  # Sends X-Code as response, self.command == POST/GET/OPTION
  self.wfile.write((f"HTTP/1.1 {code} {text}\r\n").encode('utf-8'))
  self.send_header('Content-Length',size)
  self.send_header('Connection','close')
  for k,v in self._headers.items():
   try:
    self.send_header(k,v)
   except:
    self.send_header('X-Header-Error',k)
  self.end_headers()

 #
 def do_OPTIONS(self):
  self._headers.update({'Access-Control-Allow-Headers':'X-Token,Content-Type','Access-Control-Allow-Origin':'*'})
  self.header(200,'OK',0)

 #
 def do_GET(self):
  if self.headers.get('If-None-Match') and self.headers['If-None-Match'][3:-1] == str(__build__):
   self.header(304,'Not Modified',0)
  elif self.path != '/':
   path,_,query = unquote(self.path[1:]).rpartition('/')
   file,_,_ = query.partition('?')
   # split query in file and params
   if path[:5] != 'files':
    fullpath = ospath.join(self._ctx.site,path,file)
   elif path == 'files':
    fullpath = ospath.join(self._ctx.config['files'][file])
    file = ''
   else:
    param,_,rest = path[6:].partition('/')
    fullpath = ospath.join(self._ctx.config['files'][param],rest,file)
   self._ctx.analytics('files', path, file)
   if file == '' and ospath.isdir(fullpath):
    self._headers['Content-type']='text/html; charset=utf-8'
    try:
     _, _, filelist = next(walk(fullpath), (None, None, []))
     body = ('<BR>'.join(f"<A HREF='{file}'>{file}</A>" for file in filelist)).encode('utf-8')
     self.header(200,'OK',len(body))
     self.wfile.write(body)
    except Exception as e:
     self._headers.update({'X-Exception':str(e),'Content-type':'text/html; charset=utf-8'})
     self.header(404,'Not Found',0)
   elif ospath.isfile(fullpath):
    _,_,ftype = file.rpartition('.')
    if ftype == 'js':
     self._headers.update({'Content-type':'application/javascript; charset=utf-8','Cache-Control':'public, max-age=0','ETag':f'W/"{__build__}"'})
    elif ftype == 'css':
     self._headers.update({'Content-type':'text/css; charset=utf-8','Cache-Control':'public, max-age=0','ETag':f'W/"{__build__}"'})
    elif ftype == 'html':
     # self._headers['Content-type']='text/html; charset=utf-8'
     self._headers.update({'Content-type':'text/html; charset=utf-8','Cache-Control':'public, max-age=0','ETag':f'W/"{__build__}"'})
    elif ftype == 'txt':
     self._headers.update({'Content-type':'text/plain; charset=utf-8','Cache-Control':'public, max-age=0','ETag':f'W/"{__build__}"'})
    else:
     self._headers.update({'Cache-Control':'public, max-age=0','ETag':f'W/"{__build__}"'})
    try:
     with open(fullpath, 'rb') as file:
      self.header(200,'OK',osstat(fullpath).st_size)
      for chunk in self.__read_generator(file):
       self.wfile.write(chunk)
    except Exception as e:
     self._headers.update({'X-Exception':str(e),'Content-type':'text/html; charset=utf-8'})
     try:
      self.header(404,'Not Found',0)
     except:
      pass
   else:
    self.header(404,'Not Found',0)
  else:
   self._headers.update({'Location':'index.html'})
   self.header(301,'Moved Permanently',0)

 #
 def do_POST(self):
  """ Route request to the right function /<path>/mod_fun?get"""
  path,_,query = self.path[1:].partition('/')
  if path == 'api':
   try:
    cookies = dict([c.split('=') for c in self.headers['Cookie'].split('; ')])
    tid = self._ctx.tokens[cookies['rims']]['id']
   except:
    self._headers.update({'X-Code':401})
    self._ctx.log(f"API Cookie error: {self.client_address[0]} sent non-matching cookie in call: {self.path}")
   else:
    self.api(query,tid)
  elif path == 'internal':
   if self.headers.get('X-Token') == self._ctx.token:
    self.api(query,0)
   else:
    self._headers.update({'X-Code':401})
  elif path == 'front':
   self._headers.update({'Content-type':'application/json; charset=utf-8','Access-Control-Allow-Origin':"*"})
   output = {'message':"Welcome to the Management Portal",'title':'Portal'}
   output.update(self._ctx.config['site'].get('portal'))
   self._body = dumps(output).encode('utf-8')
  elif path == 'auth':
   self.auth()
  elif path == 'vizmap':
   # Bypass auth for visualize
   self._headers.update({'Content-type':'application/json; charset=utf-8','Access-Control-Allow-Origin':"*"})
   try:
    length = int(self.headers.get('Content-Length',0))
    args = loads(self.rfile.read(length).decode()) if length else {}
   except Exception as e:
    output = {'status':'NOT_OK','info':str(e)}
   else:
    if args.get('id'):
     module = import_module('rims.api.visualize')
     output = getattr(module,"show", lambda x,y: None)(self._ctx, {'id':args['id']})
    elif args.get('device'):
     module = import_module('rims.api.device')
     output = getattr(module,"management", lambda x,y: None)(self._ctx, {'id':args['device']})
    else:
     output = {'status':'NOT_OK','info':'no suitable argument','data':{}}
   self._body = dumps(output).encode('utf-8')
  elif path == 'register':
   # Register uses internal tokens
   if self.headers.get('X-Token') == self._ctx.token:
    self._headers.update({'Content-type':'application/json; charset=utf-8'})
    try:
     length = int(self.headers.get('Content-Length',0))
     args = loads(self.rfile.read(length).decode()) if length else {}
     params = {'node':args['id'],'url':f"http://{self.client_address[0]}:{args['port']}"}
    except Exception as e:
     output = {'status':'NOT_OK','info':str(e)}
    else:
     output = {'status':'OK'}
     with self._ctx.db as db:
      output['update'] = (db.execute("INSERT INTO nodes(node, url) VALUES ('%(node)s','%(url)s') ON DUPLICATE KEY UPDATE url = '%(url)s'"%params) > 0)
     self._ctx.log(f"Registered node {args['id']}: update:{output['update']}")
    self._body = dumps(output).encode('utf-8')
   else:
    self._headers.update({'X-Code':401})
  else:
   self._headers.update({'X-Code':404})
  code = self._headers.pop('X-Code',200)
  self.header(code,self.responses.get(code,('Other','Server specialized return code'))[0],len(self._body))
  self.wfile.write(self._body)

 #
 def api(self,api,tid):
  """ API serves the REST functions x.y.z.a:<port>/api/module-path/function """
  (mod,_,fun) = api.rpartition('/')
  self._headers.update({'X-Module':mod, 'X-Function':fun ,'X-User-ID':tid, 'Content-Type':"application/json; charset=utf-8",'Access-Control-Allow-Origin':"*",'X-Route':self.headers.get('X-Route',self._ctx.node if mod != 'master' else 'master')})
  try:
   length = int(self.headers.get('Content-Length',0))
   if length:
    raw = self.rfile.read(length).decode()
    header,_,_ = self.headers['Content-Type'].partition(';')
    if header == 'application/json':
     args = loads(raw)
    elif header == 'application/x-www-form-urlencoded':
     args = { k: l[0] for k,l in parse_qs(raw, keep_blank_values=1).items() }
    else:
     args = {}
   else:
    args = {}
  except:
   args = {}
  restlog = self._ctx.config['logging']['rest']
  if restlog['enabled'] and self.headers.get('X-Log','true') == 'true':
   logstring = f"%s: {api} '%s' {tid}@{self._headers['X-Route']}\n"%(strftime('%Y-%m-%d %H:%M:%S', localtime()), dumps(args) if api != "system/worker" else "N/A")
   if self._ctx.debug:
    stdout.write(logstring)
   else:
    with open(restlog['file'], 'a') as f:
     f.write(logstring)
  try:
   self._ctx.analytics('modules',mod,fun)
   if self._headers['X-Route'] == self._ctx.node:
    module = import_module(f"rims.api.{mod.replace('/','.')}")
    self._body = dumps(getattr(module,fun, lambda x,y: None)(self._ctx, args)).encode('utf-8')
   else:
    self._body = self._ctx.rest_call(f"{self._ctx.nodes[self._headers['X-Route']]['url']}/internal/{api}", aArgs = args, aHeader = {'X-Token':self._ctx.token}, aDecode = False, aDataOnly = True, aMethod = 'POST')
  except RestException as e:
   self._headers.update({'X-Args':args, 'X-Exception':e.exception, 'X-Code':e.code, 'X-Info':e.info})
  except Exception as e:
   self._headers.update({'X-Args':args, 'X-Exception':type(e).__name__, 'X-Code':600, 'X-Info':','.join(map(str,e.args))})
   if self._ctx.debug:
    for n,v in enumerate(format_exc().split('\n')):
     self._headers[f"X-Debug-{n:02}"] = v

 ################### AUTHENTICATION #################
 #
 def auth(self):
  """ Authenticate using node function. """
  self._headers.update({'Content-type':'application/json; charset=utf-8','X-Code':401,'Access-Control-Allow-Origin':"*"})
  output = {'status':'NOT_OK'}
  try:
   length = int(self.headers.get('Content-Length',0))
   args = loads(self.rfile.read(length).decode()) if length else {}
   if args.get('verify'):
    token = args['verify']
   elif args.get('destroy'):
    token = args['destroy']
   else:
    username, password = args['username'], args['password']
  except Exception as e:
   output['info'] = {'argument':str(e)}
  else:
   if self._ctx.node == 'master':
    if 'verify' in args:
     if self._ctx.tokens.get(token):
      entry = self._ctx.tokens[token]
      # Check if client moved, update local table then...
      if entry['ip'] != args.get('ip',self.client_address[0]):
       entry['ip'] = args.get('ip',self.client_address[0])
      output = {'status':'OK','id':entry['id'],'ip':entry['ip'],'alias':entry['alias'],'token':token,'class':entry['class'],'expires':entry['expires'].strftime('%a, %d %b %Y %H:%M:%S %Z')}
      self._headers['X-Code'] = 200
    elif 'destroy' in args:
     info = self._ctx.tokens.pop(token,None)
     if info:
      self._ctx.queue_function(self._ctx.auth_exec, info['alias'], info['ip'], 'invalidate')
      with self._ctx.db as db:
       if not db.execute(f"DELETE FROM user_tokens WHERE token = '{token}'"):
        self._ctx.log(f"Authentication: destroying non-existent token requested from {self.client_address[0]}")
      output['status'] = 'OK'
      self._headers['X-Code'] = 200
    else:
     passcode = crypt(password, f"$1${self._ctx.config['salt']}$").split('$')[3]
     with self._ctx.db as db:
      if db.query(f"SELECT id, class, theme FROM users WHERE alias = '{username}' and password = '{passcode}'"):
       expires = datetime.now(timezone.utc) + timedelta(days=5)
       output.update(db.get_row())
       output.update({'alias':username,'ip':args.get('ip',self.client_address[0]),'expires':expires.strftime('%a, %d %b %Y %H:%M:%S %Z')})
       for k,v in self._ctx.tokens.items():
        # Existing id/ip, just update token expiration and return existing
        if v['id'] == output['id'] and v['ip'] == output['ip']:
         output['token'] = k
         v['expires'] = expires
         db.execute(f"UPDATE user_tokens SET created = NOW() WHERE token = '{k}'")
         break
       else:
        # New token generated, update all tables (token, database and auth servers)
        output['token'] = self.__randomizer(16)
        db.execute("INSERT INTO user_tokens (user_id,token,source_ip) VALUES(%(id)s,'%(token)s',INET6_ATON('%(ip)s'))"%output)
        self._ctx.tokens[output['token']] = {'id':output['id'],'alias':username,'expires':expires,'ip':output['ip'],'class':output['class']}
        self._ctx.queue_function(self._ctx.auth_exec, username, output['ip'], 'authenticate')
       output['status'] = 'OK'
       self._headers['X-Code'] = 200
      else:
       output['info'] = {'authentication':'username and password combination not found','username':username,'passcode':passcode}
       self._ctx.log(f"Authentication failure for {username} from {args.get('ip',self.client_address[0])}")
   else:
    try:
     args['ip'] = self.client_address[0]
     output = self._ctx.rest_call(f"{self._ctx.config['master']}/auth", aArgs = args, aDataOnly = True, aMethod = 'POST')
     if 'destroy' not in args:
      self._ctx.tokens[output['token']] = {'id':output['id'],'alias':output['alias'],'expires':datetime.strptime(output['expires'],"%a, %d %b %Y %H:%M:%S %Z"),'ip':output['ip']}
      self._headers['X-Code'] = 200
     elif output['status'] == 'OK':
      self._ctx.tokens.pop(args['destroy'],None)
      self._headers['X-Code'] = 200
    except Exception as e:
     output = {'info':e.args[0]}
     self._headers['X-Code'] = e.args[0]['code']
  output['node'] = self._ctx.node
  self._body = dumps(output).encode('utf-8')

########################################### Threads ###########################################
#
#
class TimeOutException(Exception):

  def __init__(self, *args):
   self.time = args[0]

  def __str__(self):
   return f"TimeOut({self.time})"

#
#
class Worker(Thread):

 def __init__(self, aContext, aAbort, aNumber, aQueue):
  Thread.__init__(self)
  self._n      = aNumber
  self.func    = None
  self._abort  = aAbort
  self._idle   = Event()
  self._queue  = aQueue
  self._ctx    = aContext.clone()
  self._time   = None
  self.daemon  = True
  self.name    = f"Worker({aNumber:02})"
  self.start()

 def db_analytics(self):
  return self._ctx.db.count.items()

 def is_idle(self):
  return self._idle.is_set()

 # Returns starting epoch
 def runtime(self):
  return self._time if self._ctx.debug and self._time else 0

 def run(self):
  ctx, queue, abort, idle = self._ctx, self._queue, self._abort, self._idle
  while not abort.is_set():
   try:
    self.func = None
    idle.set()
    (func, api, sema, output, args, kwargs) = queue.get(True)
    idle.clear()
    self.func = repr(func)
    if ctx.debug:
     # stdout.write(f"{self.name} - {self.func} => starting\n")
     self._time = int(time())
    result = func(*args,**kwargs) if not api else func(ctx, args)
   except Exception as e:
    ctx.log(f"{self.name} - ERROR: {self.func} => {e}")
    if ctx.debug:
     for n,v in enumerate(format_exc().split('\n')):
      stdout.write(f"{self.name} - DEBUG-{n:02} => {v}\n")
   else:
    if output:
     parts = self.func.split()
     ctx.log(f"{self.name} - {parts[1] if parts[0] == '<function' else parts[2]} => {dumps(result)}")
   finally:
    queue.task_done()
    if sema:
     sema.release()
    if ctx.debug:
     # stdout.write(f"{self.name} - {self.func} => finished ({int(time()) - self._time}s)\n")
     self._time = None
  return False

#
#
class SocketServer(Thread):

 def __init__(self, aContext, aAbort, aName, aAddress, aSocket):
  Thread.__init__(self)
  self.name   = f"SocketServer({aName}"
  self.daemon = True
  self._abort = aAbort
  httpd = HTTPServer(aAddress, SessionHandler, False)
  self._httpd = httpd
  httpd.socket = aSocket
  httpd.timeout = 0.5
  httpd._ctx = self._ctx = aContext.clone()
  httpd.server_bind = httpd.server_close = lambda self: None
  self.start()

 def db_analytics(self):
  return self._ctx.db.count.items()

 def run(self):
  abort = self._abort
  httpd = self._httpd
  while not abort.is_set():
   try:
    httpd.handle_request()
   except:
    pass
   #except Exception as e: stdout.write(f"Error: {self.name} => {e}")
  return False

########################################### House Keeping ###########################################
#
class HouseKeeping(Thread):
 """Persistent thread for continuous house keeping"""

 def __init__(self, aContext, aAbort):
  Thread.__init__(self)
  self.name = 'House Keeping'
  self.daemon = True
  self._abort = aAbort
  self._ctx = aContext.clone()
  self.start()

 #
 def run(self):
  abort = self._abort
  sleep(int(self._ctx.config.get('startupdelay',10)))
  while not abort.is_set():
   try:
    self.house_keeping()
   except Exception as e:
    stdout.write(f'House keeping error: {str(e)}')
   finally:
    sleep(1800)
  return False

 #
 def house_keeping(self):
  """ House keeping should do all the things that are supposed to be regular (phase out old tokens, memory mangagement etc)"""
  ctx = self._ctx
  now = datetime.now(timezone.utc)

  # Worker monitoring
  active = 0
  for w in ctx.workers_active():
   active += 1
   if w[2] >= 60:
    ctx.log(f'{w[0]}/{w[3]} stuck for {w[2]} seconds with {w[1]}')

  # Token management
  expired = []
  remain = []
  for k,v in ctx.tokens.items():
   if now > v['expires']:
    expired.append(k)
   else:
    remain.append(v)
  for t in expired:
   ctx.tokens.pop(t,None)

  # Authentication management, centralized
  if ctx.node == 'master' and remain:
   with ctx.db as db:
    db.query(f"SELECT id,alias FROM users WHERE id IN ({','.join([str(v['id']) for v in remain])})")
    alias = {x['id']:x['alias'] for x in db.get_rows()}
   users = [{'ip':v['ip'],'alias':alias[v['id']],'timeout':min(int((v['expires']-now).total_seconds()),7200)} for v in remain]
   ctx.log(f"Resyncing {len(users)} users")
   for infra in [{'service':v['service'],'node':v['node'],'id':k} for k,v in ctx.services.items() if v['type'] == 'AUTHENTICATION']:
    ctx.node_function(infra['node'], f"services.{infra['service']}", 'sync')(aArgs = {'id':infra['id'],'users':users})
  garbage_collect()
  ctx.log(f"House keeping => OK ({active})")
  return True

