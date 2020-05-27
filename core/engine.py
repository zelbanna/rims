"""System engine"""
__author__ = "Zacharias El Banna"
__version__ = "6.5"
__build__ = 332
__all__ = ['Context']

from crypt import crypt
from datetime import datetime, timedelta, timezone
from functools import partial
from gc import collect as garbage_collect
from http.server import BaseHTTPRequestHandler, HTTPServer
from importlib import import_module, reload as reload_module
from json import loads, load, dumps
from os import path as ospath, getpid, walk, stat as osstat
from random import choice
from ssl import SSLContext, SSLError, PROTOCOL_SSLv23
from string import ascii_uppercase, digits
from sys import stdout
from threading import Thread, Event, BoundedSemaphore, enumerate as thread_enumerate
from time import localtime, time, sleep, strftime
from traceback import format_exc
from urllib.parse import unquote, parse_qs
from rims.core.common import DB, rest_call, Scheduler

##################################################### Context #######################################################
#
# Main state object, contains config, workers, modules and calls etc..
#
class Context(object):

 def __init__(self,aConfig):
  """ Context init - create the infrastructure but populate later
  - Consume config file
  - Set node ID
  - Prepare database and workers
  - initiate the 'kill' switch
  - create datastore (i.e. dict) for nodes, services
  """
  from queue import Queue
  self.config = aConfig
  self._queue = Queue(0)
  self._abort = Event()
  self._kill  = Event()
  self._sock  = None
  self._ssock = None
  self._workers = []
  self._servers = []
  self._scheduler = Scheduler(self._abort,self._queue)
  self._analytics = {'files':{},'modules':{}}

  database   = self.config.get('database')
  self.db    = DB(database['name'],database['host'],database['username'],database['password']) if database else None
  self.node  = self.config['id']
  self.token = self.config.get('token')
  self.path  = ospath.abspath(ospath.join(ospath.dirname(__file__), '..'))
  self.site  = ospath.join(self.path,'site')
  self.nodes = {}
  self.tokens = {}
  self.services = {}
  self.rest_call = rest_call
  self.config['salt'] = self.config.get('salt','WBEUAHfO')
  self.config['mode'] = self.config.get('mode','api')
  self.config['workers'] = self.config.get('workers',20)
  self.config['logging'] = self.config.get('logging',{})
  self.config['logging']['rest']   = self.config['logging'].get('rest',{'enabled':False,'file':None})
  self.config['logging']['system'] = self.config['logging'].get('system',{'enabled':False,'file':None})
  if self.config.get('site'):
   for type in ['menuitem','resource']:
    for k,item in self.config['site'].get(type,{}).items():
     for tp in ['module','frame','tab']:
      if tp in item:
       item['type'] = tp
       break
  else:
   self.log("No site defined")

 #################### MAIN MACHINERY ##################
 #
 def clone(self):
  """ Clone itself and non thread-safe components, avoid using copy and having to copy everything manually... """
  from copy import copy
  ctx_new = copy(self)
  database = self.config.get('database')
  ctx_new.db = DB(database['name'],database['host'],database['username'],database['password']) if database else None
  return ctx_new

 #
 def environment(self,aNode):
  """ Function retrieves all central environment for a certain node, or itself if node is given"""
  if len(aNode) == 0 or aNode is None:
   env = {'nodes':self.nodes,'services':self.services,'config':self.config,'tasks':self.scheduler_status(),'site':(len(self.config['site']) > 0),'version':__version__,'build':__build__}
  elif self.config.get('database'):
   env = {'tokens':{}}
   with self.db as db:
    db.do("SELECT id, node, url FROM nodes")
    env['nodes']   = {x['node']:{'id':x['id'],'url':x['url']} for x in db.get_rows()}
    db.do("SELECT servers.id, node, st.service, st.type FROM servers LEFT JOIN service_types AS st ON servers.type_id = st.id")
    env['services'] = {x['id']:{'node':x['node'],'service':x['service'],'type':x['type']} for x in db.get_rows()}
    db.do("SELECT tasks.id, module, function, args, frequency, output FROM tasks LEFT JOIN nodes ON nodes.id = tasks.node_id WHERE node = '%s'"%aNode)
    env['tasks']   = db.get_rows()
    for task in env['tasks']:
     task['output'] = (task['output']== 'true')
    db.do("DELETE FROM user_tokens WHERE created + INTERVAL 5 DAY < NOW()")
    db.do("SELECT users.id, ut.token, users.alias, ut.created + INTERVAL 5 DAY as expires, INET_NTOA(ut.source_ip) AS ip, users.class FROM user_tokens AS ut LEFT JOIN users ON users.id = ut.user_id ORDER BY created DESC")
    env['tokens'] = {x['token']:{'id':x['id'], 'alias':x['alias'],'expires':x['expires'].replace(tzinfo=timezone.utc), 'ip':x['ip'], 'class':x['class']} for x in db.get_rows()}
   env['version'] = __version__
   env['build'] = __build__
  else:
   env = self.rest_call("%s/internal/system/environment"%self.config['master'], aHeader = {'X-Token':self.token}, aArgs = {'node':aNode,'build':__build__}, aDataOnly = True)
   env['nodes']['master']['url'] = self.config['master']
   for k,v in env['tokens'].items():
    v['expires'] = datetime.strptime(v['expires'],"%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc)
  return env

 #
 def load(self):
  """ Load environment from DB or retrieve from master node. Add tasks to queue, return true if system loaded successfully"""
  try:
   env = self.environment(self.node)
  except Exception as e:
   print("Load environment error: %s"%str(e))
   return False
  else:
   self.log("______ Loading environment - version: %s mode: %s ______"%(__build__,self.config['mode']))
   self.nodes.update(env['nodes'])
   self.services.update(env['services'])
   self.tokens.update(env.get('tokens',{}))
   for task in env['tasks']:
    try:    freq = int(task.pop('frequency'))
    except: freq = 0
    self.log("Adding task: %(module)s/%(function)s"%task)
    self.schedule_api_task(task['module'],task['function'],freq, args = loads(task['args']), output = (task['output'] in ['true',True]))
   self.schedule_function(self.house_keeping, 'ctx_house_keeping', 10, 3600)
   if __build__ != env['build']:
    self.log("Build mismatch between master and node: %s != %s"%(__build__,env['build']))
   return True

 #
 def start(self):
  """ Start "moving" parts of context, workers and signal handlers to start processing incoming requests and scheduled tasks """
  from signal import signal, SIGINT, SIGUSR1, SIGUSR2
  from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

  def create_socket(port):
   """ Create a (secure) socket """
   addr = ("0.0.0.0", port)
   sock = socket(AF_INET, SOCK_STREAM, 0)
   sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
   sock.bind(addr)
   sock.listen(5)
   return (addr,sock)

  try:
   self._workers = [QueueWorker(n, self._abort, self._queue, self) for n in range(self.config['workers'])]
   self._abort.clear()
   self._scheduler.start()

   servers = 0
   if (self.config.get('port')):
    self.log("Starting HTTP server at: %s"%self.config['port'])
    addr,sock = create_socket(int(self.config['port']))
    self._sock = sock
    self._servers.extend(ServerWorker(n,addr,sock,self) for n in range(servers,servers+4))
    servers = 4
   if (self.config.get('ssl')):
    ssl_config = self.config['ssl']
    self.log("Starting HTTPS server at: %s"%ssl_config['port'])
    context = SSLContext(PROTOCOL_SSLv23)
    context.load_cert_chain(ssl_config['certfile'], keyfile=ssl_config['keyfile'], password=ssl_config.get('password'))
    addr,ssock = create_socket(int(ssl_config['port']))
    self._ssock = context.wrap_socket(ssock, server_side=True)
    self._servers.extend(ServerWorker(n,addr,self._ssock,self) for n in range(servers,servers+4))

   for sig in [SIGINT, SIGUSR1, SIGUSR2]:
    signal(sig, self.signal_handler)
  except Exception as e:
   print("Starting error - check IP and SSL settings: %s"%str(e))
   return False
  else:
   return True

 #
 def close(self):
  """ Abort set abort state and inject dummy tasks to kill off workers. There might be running tasks so don't add more than enough. Finally set kill to inform that we are done """
  def dummy(): pass
  self._abort.set()
  try: self._sock.close()
  except: pass
  finally: self._sock = None
  try: self._ssock.close()
  except: pass
  finally: self._ssock = None
  while self.workers_alive() > 0:
   for x in range(0,self.workers_alive() - self._queue.qsize()):
    self._queue.put((dummy,False,None,False,[],{}))
   while not self._queue.empty() and self.workers_alive() > 0:
    sleep(0.1)
    self._workers = [x for x in self._workers if x.is_alive()]
  self._kill.set()

 #
 def wait(self):
  """ expose a 'wait' method for graceful shutdown """
  self._kill.wait()

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
   data['services'] = self.services
   data['tokens'] = {k:{'id':v['id'],'alias':v['alias'],'ip':v['ip'],'class':v['class'],'expires':v['expires'].strftime("%a, %d %b %Y %H:%M:%S %Z")} for k,v in self.tokens.items()}
   print("System Info:\n_____________________________\n%s\n_____________________________"%(dumps(data,indent=2, sort_keys=True)))

 ######################## TOOLS #####################
 #
 def debugging(self):
  """ Return debug status """
  return (self.config['mode'] == 'debug')

 #
 def log(self,aMsg):
  """ Log a system message """
  syslog = self.config['logging']['system']
  if syslog['enabled']:
   with open(syslog['file'], 'a') as f:
    f.write(str("%s: %s\n"%(strftime('%Y-%m-%d %H:%M:%S', localtime()), aMsg)))

 #
 def house_keeping(self):
  """ House keeping should do all the things that are supposed to be regular (phase out old tokens, memory mangagement etc)"""
  ret = {}
  now = datetime.now(timezone.utc)
  expired = []
  for k,v in self.tokens.items():
   if now > v['expires']:
    expired.append(k)
  ret['expired'] = len(expired)
  for t in expired:
   self.tokens.pop(t,None)
  ret['auth'] = self.auth_sync()
  ret['collected'] = garbage_collect()
  return ret

 ################# API AND INTERNAL FUNCTIONS ##############
 #
 def node_function(self, aNode, aModule, aFunction, **kwargs):
  """
  Node function freezes a function (or convert to a REST call at node) with enough info so that the returned lambda can be used multiple times AND interchangably.
  For this to work the argument to the function will have to be keyworded/**kwargs because if using REST then rest_call function picks everything from kwargs
  """
  if self.node != aNode:
   kwargs['aDataOnly'] = True
   kwargs['aHeader'] = kwargs.get('aHeader',{})
   kwargs['aHeader']['X-Token'] = self.token
   try: ret = partial(self.rest_call,"%s/internal/%s/%s"%(self.nodes[aNode]['url'],aModule.replace('.','/'),aFunction), **kwargs)
   except Exception as e:
    self.log("Node Function REST failure: %s/%s@%s (%s) => %s"%(aModule,aFunction,aNode,dumps(kwargs),str(e)))
    ret = {'status':'NOT_OK','info':'NODE_FUNCTION_FAILURE: %s'%str(e)}
  else:
   module = import_module("rims.api.%s"%aModule)
   fun = getattr(module,aFunction,lambda aCTX,aArgs: None)
   ret = partial(fun,self)
  return ret

 #
 def module_reload(self):
  """ Reload modules and return which ones were reloaded """
  from sys import modules as sys_modules
  from types import ModuleType
  modules = {x:sys_modules[x] for x in sys_modules.keys() if x.startswith('rims.')}
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
 def report(self):
  """ Create a report of system and activities """
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
  'Workers pool':self.workers_alive(),
  'Workers idle':self.workers_idles(),
  'Workers queue':self.queue_size(),
  'Servers':self.workers_servers(),
  'Active Tokens':len(self.tokens),
  'Database':', '.join("%s:%s"%(k.lower(),v) for k,v in db_counter.items()),
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

 ################# AUTHENTICATION ################
 #
 def auth_sync(self):
  """ Synchronizes external services auth entries with user tokens """
  with self.db as db:
   db.do("SELECT id,alias FROM users WHERE id IN (%s)"%','.join([str(v['id']) for v in self.tokens.values()]))
   alias = {x['id']:x['alias'] for x in db.get_rows()}
  users = [{'ip':v['ip'],'alias':alias[v['id']]} for v in self.tokens.values()]
  for infra in [{'service':v['service'],'node':v['node'],'id':k} for k,v in self.services.items() if v['type'] == 'AUTHENTICATION']:
   self.node_function(infra['node'], "services.%s"%infra['service'], 'sync')(aArgs = {'id':infra['id'],'users':users})
  return len(users)

 #
 def auth_exec(self, aAlias, aIP, aOP):
  """ 'authenticate' or 'invalidate' alias and ip with external services"""
  for infra in [{'service':v['service'],'node':v['node']} for v in self.services.values() if v['type'] == 'AUTHENTICATION']:
   res = self.node_function(infra['node'], "services.%s"%infra['service'], aOP)(aArgs = {'alias':aAlias, 'ip': aIP})
   self.log("Authentication service for '%s' (%s %s@%s) => %s (%s)"%(aAlias, aOP, infra['service'], infra['node'], res['status'], res.get('info','N/A')))
  return True

 #################### QUEUE #####################
 #
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
  sema = BoundedSemaphore(nworkers)
  for elem in aList:
   self.queue_semaphore(aFunction, sema, elem)
  for i in range(nworkers):
   sema.acquire()

 def queue_size(self):
  """ Return the current queue size """
  return self._queue.qsize()

 def semaphore(self,aSize):
  """ Generate a semaphor """
  return BoundedSemaphore(aSize)

 ################## STATUS TOOLS ################
 #
 def workers_alive(self):
  return len([w for w in self._workers if w.is_alive()])

 def workers_idles(self):
  return len([w for w in self._workers if w._idle.is_set()])

 def workers_servers(self):
  return len([s for s in self._servers if s.is_alive()])

 #################### SCHEDULING ################
 #
 def schedule_api(self, aFunction, aName, aDelay, aFrequency = 0, **kwargs):
  self._scheduler.add_delayed((aFunction, True, None, kwargs.get('output',False), kwargs.get('args',{}), None), aName, aDelay, aFrequency)

 def schedule_api_task(self, aModule, aFunction, aFrequency = 0, **kwargs):
  try:
   mod = import_module("rims.api.%s"%aModule)
   func = getattr(mod, aFunction, None)
  except:
   self.log("WorkerPool ERROR: adding task failed (%s/%s)"%(aModule,aFunction))
   return False
  else:
   if aFrequency > 0:
    self._scheduler.add_periodic((func, True, None, kwargs.get('output',False), kwargs.get('args',{}), None),"%s/%s"%(aModule,aFunction),aFrequency)
   else:
    self._queue.put((func, True, None, kwargs.get('output',False), kwargs.get('args',{}), None))
   return True

 def schedule_api_periodic(self, aFunction, aName, aFrequency, **kwargs):
  self._scheduler.add_periodic((aFunction, True, None, kwargs.get('output',False), kwargs.get('args',{}), None), aName, aFrequency)

 def schedule_function(self, aFunction, aName, aDelay, aFrequency = 0, **kwargs):
  self._scheduler.add_delayed((aFunction, False, None, kwargs.pop('output',False), kwargs.pop('args',{}), kwargs), aName, aDelay, aFrequency)

 def scheduler_status(self):
  return [(e[1]['name'],e[1]['frequency'],e[0]) for e in self._scheduler.events()]

#
#
################################################### Session Handler #####################################################
#
#
class SessionHandler(BaseHTTPRequestHandler):

 def __init__(self, *args, **kwargs):
  self._headers = {'X-Powered-By':'RIMS Engine %s.%s'%(__version__,__build__),'Date':self.date_time_string()}
  self._body = b'null'
  self._ctx = args[2]._ctx
  BaseHTTPRequestHandler.__init__(self,*args, **kwargs)

 #
 def __read_generator(self,fd, size = 1024):
  while True:
   chunk = fd.read(size)
   if not chunk:
    break
   yield chunk

 #
 def __randomizer(self, aLength):
  return ''.join(choice(ascii_uppercase + digits) for _ in range(aLength))

 #
 def header(self,code,text,size):
  # Sends X-Code as response, self.command == POST/GET/OPTION
  self.wfile.write(('HTTP/1.1 %s %s\r\n'%(code,text)).encode('utf-8'))
  self.send_header('Content-Length',size)
  self.send_header('Connection','close')
  for k,v in self._headers.items():
   try: self.send_header(k,v)
   except: self.send_header('X-Header-Error',k)
  self.end_headers()

 #
 def do_OPTIONS(self):
  self._headers.update({'Access-Control-Allow-Headers':'X-Token,Content-Type','Access-Control-Allow-Origin':'*'})
  self.header('200','OK',0)

 #
 def do_GET(self):
  if self.headers.get('If-None-Match') and self.headers['If-None-Match'][3:-1] == str(__build__):
   self.header('304','Not Modified',0)
  elif self.path != '/':
   path,_,query = unquote(self.path[1:]).rpartition('/')
   file,_,_ = query.partition('?')
   # split query in file and params
   if not path[:5] == 'files':
    fullpath = ospath.join(self._ctx.site,path,file)
   elif path == 'files':
    fullpath = ospath.join(self._ctx.config['files'][file])
    file = ''
   else:
    param,_,rest = path[6:].partition('/')
    fullpath = ospath.join(self._ctx.config['files'][param],rest,file)
   self._ctx.analytics('files', path, file)
   # print("FULLPATH:%s"%fullpath)
   if file == '' and ospath.isdir(fullpath):
    self._headers['Content-type']='text/html; charset=utf-8'
    try:
     _, _, filelist = next(walk(fullpath), (None, None, []))
     body = ("<BR>".join("<A HREF='{0}'>{0}</A>".format(file) for file in filelist)).encode('utf-8')
     self.header(200,'OK',len(body))
     self.wfile.write(body)
    except:
     self._headers.update({'X-Exception':str(e),'Content-type':'text/html; charset=utf-8'})
     self.header(404,'Not Found',0)
   elif ospath.isfile(fullpath):
    _,_,ftype = file.rpartition('.')
    if ftype == 'js':
     self._headers.update({'Content-type':'application/javascript; charset=utf-8','Cache-Control':'public, max-age=0','ETag':'W/"%s"'%__build__})
    elif ftype == 'css':
     self._headers.update({'Content-type':'text/css; charset=utf-8','Cache-Control':'public, max-age=0','ETag':'W/"%s"'%__build__})
    elif ftype == 'html':
     # self._headers['Content-type']='text/html; charset=utf-8'
     self._headers.update({'Content-type':'text/html; charset=utf-8','Cache-Control':'public, max-age=0','ETag':'W/"%s"'%__build__})
    else:
     self._headers.update({'Cache-Control':'public, max-age=0','ETag':'W/"%s"'%__build__})
    try:
     with open(fullpath, 'rb') as file:
      self.header(200,'OK',osstat(fullpath).st_size)
      for chunk in self.__read_generator(file):
       self.wfile.write(chunk)
    except Exception as e:
     self._headers.update({'X-Exception':str(e),'Content-type':'text/html; charset=utf-8'})
     try: self.header(404,'Not Found',0)
     except: pass
   else:
    self.header(404,'Not Found',0)
  else:
   self._headers.update({'Location':'index.html'})
   self.header('301','Moved Permanently',0)

 #
 def do_POST(self):
  """ Route request to the right function /<path>/mod_fun?get"""
  path,_,query = self.path[1:].partition('/')
  if path == 'api':
   try:
    cookies = dict([c.split('=') for c in self.headers['Cookie'].split('; ')])
    id = self._ctx.tokens[cookies['rims']]['id']
   except:
    self._headers.update({'X-Code':401})
    self._ctx.log("API Cookie error: %s sent non-matching cookie in call: %s"%(self.client_address[0],self.path))
   else:
    self.api(query,id)
  elif path == 'internal':
   if self.headers.get('X-Token') == self._ctx.token: self.api(query,0)
   else: self._headers.update({'X-Code':401})
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
    args = loads(self.rfile.read(length).decode()) if length > 0 else {}
   except Exception as e:
    output = {'status':'NOT_OK','info':str(e)}
   else:
    if args.get('id'):
     module = import_module("rims.api.visualize")
     output = getattr(module,"show", lambda x,y: None)(self._ctx, {'id':args['id']})
    elif args.get('device'):
     module = import_module("rims.api.device")
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
     args = loads(self.rfile.read(length).decode()) if length > 0 else {}
     params = {'node':args['id'],'url':"http://%s:%s"%(self.client_address[0],args['port'])}
    except Exception as e:
     output = {'status':'NOT_OK','info':str(e)}
    else:
     output = {'status':'OK'}
     with self._ctx.db as db:
      output['update'] = (db.do("INSERT INTO nodes(node, url) VALUES ('%(node)s','%(url)s') ON DUPLICATE KEY UPDATE url = '%(url)s'"%params) > 0)
     self._ctx.log("Registered node %s: update:%s"%(args['id'],output['update']))
    self._body = dumps(output).encode('utf-8')
   else:
    self._headers.update({'X-Code':401})
  else:
   self._headers.update({'X-Code':404})
  code = self._headers.pop('X-Code',200)
  self.header(code,self.responses.get(code,('Other','Server specialized return code'))[0],len(self._body))
  self.wfile.write(self._body)

 #
 def api(self,api,id):
  """ API serves the REST functions x.y.z.a:<port>/api/module-path/function """
  (mod,_,fun) = api.rpartition('/')
  self._headers.update({'X-Module':mod, 'X-Function':fun ,'X-User-ID':id, 'Content-Type':"application/json; charset=utf-8",'Access-Control-Allow-Origin':"*",'X-Route':self.headers.get('X-Route',self._ctx.node if not mod == 'master' else 'master')})
  try:
   length = int(self.headers.get('Content-Length',0))
   if length > 0:
    raw = self.rfile.read(length).decode()
    header,_,_ = self.headers['Content-Type'].partition(';')
    if   header == 'application/json': args = loads(raw)
    elif header == 'application/x-www-form-urlencoded': args = { k: l[0] for k,l in parse_qs(raw, keep_blank_values=1).items() }
    else: args = {}
   else:  args = {}
  except: args = {}
  if self._ctx.config['logging']['rest']['enabled'] and self.headers.get('X-Log','true') == 'true':
   logstring = str("%s: %s '%s' %s@%s\n"%(strftime('%Y-%m-%d %H:%M:%S', localtime()), api, dumps(args) if api != "system/worker" else "N/A", id, self._headers['X-Route']))
   if self._ctx.config['logging']['rest']['enabled'] == 'debug':
    stdout.write(logstring)
   else:
    with open(self._ctx.config['logging']['rest']['file'], 'a') as f:
     f.write(logstring)
  try:
   self._ctx.analytics('modules',mod,fun)
   if self._headers['X-Route'] == self._ctx.node:
    module = import_module('rims.api.%s'%mod.replace('/','.'))
    self._body = dumps(getattr(module,fun, lambda x,y: None)(self._ctx, args)).encode('utf-8')
   else:
    self._body = self._ctx.rest_call("%s/internal/%s"%(self._ctx.nodes[self._headers['X-Route']]['url'],api), aArgs = args, aHeader = {'X-Token':self._ctx.token}, aDecode = False, aDataOnly = True, aMethod = 'POST')
  except Exception as e:
   if not (isinstance(e.args[0],dict) and e.args[0].get('code')):
    self._headers.update({'X-Args':args, 'X-Exception':type(e).__name__, 'X-Code':600, 'X-Info':','.join(map(str,e.args))})
   else:
    self._headers.update({'X-Args':args, 'X-Exception':e.args[0].get('exception'), 'X-Code':e.args[0]['code'], 'X-Info':e.args[0].get('info')})
   if self._ctx.config['mode'] == 'debug':
    for n,v in enumerate(format_exc().split('\n')):
     self._headers["X-Debug-%02d"%n] = v

 ################### AUTHENTICATION #################
 #
 def auth(self):
  """ Authenticate using node function. """
  self._headers.update({'Content-type':'application/json; charset=utf-8','X-Code':401,'Access-Control-Allow-Origin':"*"})
  output = {'status':'NOT_OK'}
  try:
   length = int(self.headers.get('Content-Length',0))
   args = loads(self.rfile.read(length).decode()) if length > 0 else {}
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
     if (self._ctx.tokens.get(token)):
      entry = self._ctx.tokens[token]
      # Check if client moved, update local table then...
      if entry['ip'] != args.get('ip',self.client_address[0]):
       entry['ip'] = args.get('ip',self.client_address[0])
      output = {'status':'OK','id':entry['id'],'ip':entry['ip'],'alias':entry['alias'],'token':token,'class':entry['class'],'expires':entry['expires'].strftime("%a, %d %b %Y %H:%M:%S %Z")}
      self._headers['X-Code'] = 200
    elif 'destroy' in args:
     info = self._ctx.tokens.pop(token,None)
     if info:
      self._ctx.queue_function(self._ctx.auth_exec, info['alias'], info['ip'], 'invalidate')
      with self._ctx.db as db:
       if (db.do("DELETE FROM user_tokens WHERE token = '%s'"%token) == 0):
        self._ctx.log("Authentication: destroying non-existent token requested from %s"%self.client_address[0])
      output['status'] = 'OK'
      self._headers['X-Code'] = 200
    else:
     passcode = crypt(password, "$1$%s$"%self._ctx.config['salt']).split('$')[3]
     with self._ctx.db as db:
      if (db.do("SELECT id, class, theme FROM users WHERE alias = '%s' and password = '%s'"%(username,passcode)) == 1):
       expires = datetime.now(timezone.utc) + timedelta(days=5)
       output.update(db.get_row())
       output.update({'alias':username,'ip':args.get('ip',self.client_address[0]),'expires':expires.strftime("%a, %d %b %Y %H:%M:%S %Z")})
       for k,v in self._ctx.tokens.items():
        # Existing id/ip, just update token expiration and return existing
        if v['id'] == output['id'] and v['ip'] == output['ip']:
         output['token'] = k
         v['expires'] = expires
         db.do("UPDATE user_tokens SET created = NOW() WHERE token = '%s'"%k)
         break
       else:
        # New token generated, update all tables (token, database and auth servers)
        output['token'] = self.__randomizer(16)
        db.do("INSERT INTO user_tokens (user_id,token,source_ip) VALUES(%(id)s,'%(token)s',INET_ATON('%(ip)s'))"%output)
        self._ctx.tokens[output['token']] = {'id':output['id'],'alias':username,'expires':expires,'ip':output['ip'],'class':output['class']}
        self._ctx.queue_function(self._ctx.auth_exec, username, output['ip'], 'authenticate')
       output['status'] = 'OK'
       self._headers['X-Code'] = 200
      else:
       output['info'] = {'authentication':'username and password combination not found','username':username,'passcode':passcode}
   else:
    try:
     args['ip'] = self.client_address[0]
     output = self._ctx.rest_call("%s/auth"%(self._ctx.config['master']), aArgs = args, aDataOnly = True, aMethod = 'POST')
     if not 'destroy' in args:
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

############################################## Workers ##############################################
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
    (func, api, sema, output, args, kwargs) = self._queue.get(True)
    self._idle.clear()
    result = func(*args,**kwargs) if not api else func(self._ctx, args)
    if output:
     self._ctx.log("%s - %s => %s"%(self.name,repr(func).split()[1],dumps(result)))
   except Exception as e:
    self._ctx.log("%s - ERROR: %s => %s"%(self.name,repr(func),str(e)))
    if self._ctx.config['mode'] == 'debug':
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
  #except SSLError as e: print("SSLError: %s => %s"%(self.name,str(e)))
  #except Exception as e: print("Error: %s => %s"%(self.name,str(e)))

 def shutdown(self):
  self._httpd.shutdown()
