"""Common functions module """
__author__ = "Zacharias El Banna"

from base64 import b64encode
from time import time, sleep, strftime, localtime
from sched import scheduler
from threading import Thread, Lock, RLock, Event
from json import loads, dumps
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from urllib.error import HTTPError
from ssl import create_default_context, CERT_NONE

########################################### REST ##########################################
#
# Rest with exception and variable args handling to make it more robust and streamlined in a "one-liner"
#
#
def basic_auth(aUsername,aPassword):
 return {'Authorization':'Basic %s'%(b64encode(("%s:%s"%(aUsername,aPassword)).encode('utf-8')).decode('utf-8')) }

class RestException(Exception):
 pass

def rest_call(aURL, **kwargs):
 """ REST call function, aURL is required, then aApplication (default:'json' or 'x-www-form-urlencoded'), aArgs, aHeader (dict), aTimeout, aDataOnly (default True), aDecode (not for binary..) . Returns de-json:ed data structure and all status codes """
 try:
  head = { 'Content-Type': 'application/%s'%kwargs.get('aApplication','json'),'Accept':'application/json' }
  head.update(kwargs.get('aHeader',{}))
  if   head['Content-Type'] == 'application/json':
   args = dumps(kwargs['aArgs']).encode('utf-8') if kwargs.get('aArgs') else None
  elif head['Content-Type'] == 'application/octet-stream':
   args = kwargs['aArgs'] if kwargs.get('aArgs') else None
  elif head['Content-Type'] == 'application/xml':
   args = kwargs['aArgs'].encode('utf-8') if kwargs.get('aArgs') else None
  elif head['Content-Type'] == 'application/x-www-form-urlencoded':
   args = urlencode(kwargs['aArgs']).encode('utf-8') if kwargs.get('aArgs') else None
  else:
   raise RestException("No recognized application type (%s)"%head['Content-Type'])
  req = Request(aURL, headers = head, data = args)
  req.get_method = lambda: kwargs.get('aMethod','POST')
  if kwargs.get('aVerify',True):
   sock = urlopen(req, timeout = kwargs.get('aTimeout',20))
  else:
   ssl_ctx = create_default_context()
   ssl_ctx.check_hostname = False
   ssl_ctx.verify_mode = CERT_NONE
   sock = urlopen(req,context=ssl_ctx, timeout = kwargs.get('aTimeout',20))
  try:    data = loads(sock.read().decode()) if kwargs.get('aDecode',True) else sock.read()
  except: data = None
  res = data if kwargs.get('aDataOnly',True) else {'info':dict(sock.info()), 'code':sock.code, 'data':data }
  sock.close()
 except HTTPError as h:
  exception = { 'exception':'HTTPError', 'code':h.code, 'info':dict(h.info())}
  try:    exception['data'] = loads(h.read().decode())
  except: exception['data'] = None
 except Exception as e:
  exception = { 'exception':type(e).__name__, 'code':600, 'info':{'error':repr(e)}, 'data':None}
 else:
  exception = None
 if exception:
  raise RestException(exception)
 return res

######################################## Scheduler ######################################
#
# Single-thread scheduler for events happening withing X seconds or every X second. Uses RIMS QueueWorker for execution to maintain resource control
#
# Uses:
# - Abort (Event) as a mean to "stop the clock"
# - Queue which exposes a put method to add event task to be executed (avoiding introducing delay deue to execution)
#

class Scheduler(Thread):

 def __init__(self, aAbort, aQueue):
  Thread.__init__(self)
  self._abort = aAbort
  self._queue = aQueue
  self._signal = Event()
  self._internal = scheduler(time,sleep)
  self.daemon = True

 def __getitem__(self, aKey):
  return self._internal.queue[aKey]

 def __execute(self, aEvent):
  # print("Scheduler executing: %s"%aEvent['name'])
  self._queue.put(aEvent['task'])
  if aEvent.get('frequency',0) > 0:
   self._internal.enter(aEvent['frequency'], aEvent.get('prio',2), self.__execute, argument = (aEvent,))

 def run(self):
  """
  The thread run method most likely will not use the abort but be in a steady 'run' mode, by running it threaded we avoid blocking
  """
  while not self._abort.is_set():
   self._signal.wait()
   self._internal.run()
   self._signal.clear()
  return False

 ########################### Exposed methods #########################
 def cancel(self, aKey):
  self._internal.cancel(self._internal.queue[aKey])

 def events(self):
  """ Using internals of scheduler event model to retrieve 'task' """
  return [(x[0],x[3][0]) for x in self._internal.queue]

 def periodic_delay(self, aFrequency):
  """ Function gives a basic estimate on when to start for periodic functions.. when they fit """
  return (aFrequency - int(time())%aFrequency)

 def add_delayed(self, aTask, aName, aDelay, aFrequency = 0, aPrio = 2):
  """ Insert at 'aDelay' seconds from now with frequency 'aFrequency' """
  self._internal.enter(aDelay,aPrio, self.__execute, argument = ({'task':aTask, 'name':aName, 'frequency':aFrequency,'prio':aPrio},))
  self._signal.set()

 def add_periodic(self, aTask, aName, aFrequency, aPrio = 2):
  self._internal.enter(self.periodic_delay(aFrequency), aPrio, self.__execute, argument = ({'task':aTask, 'name':aName, 'frequency':aFrequency,'prio':aPrio},))
  self._signal.set()

############################################ Database ######################################
#
# Thread safe Database Class
# - Current Thread can reenter (RLook)
# - Other Threads will wait for resource
#
class DB(object):

 def __init__(self, aDB, aHost, aUser, aPass):
  from pymysql import connect
  from pymysql.cursors import DictCursor
  self._mods = (connect,DictCursor)
  self._db, self._host, self._user, self._pass = aDB, aHost, aUser, aPass
  self._conn, self._curs, self._dirty = None, None, False
  self._conn_lock, self._wait_lock = RLock(), Lock()
  self._conn_waiting = 0
  self._conn_in_thread = 0
  self.count = {'COMMIT':0,'CONNECT':0,'CLOSE':0,'QUERY':0,'EXECUTE':0}

 def __enter__(self):
  self.connect()
  return self

 def __exit__(self, *ctx_info):
  self.close()

 def __str__(self):
  return "Database(database=%s, host=%s, dirty=%s, count=%s)"%(self._db,self._host,self._dirty," ,".join("%s:%03d"%i for i in self.count.items()))

 def connect(self):
  with self._wait_lock:
   self._conn_waiting += 1
  self._conn_lock.acquire()
  self._conn_in_thread += 1
  self.count['CONNECT'] += 1
  if not self._conn:
   self._conn = self._mods[0](host=self._host, port=3306, user=self._user, passwd=self._pass, db=self._db, cursorclass=self._mods[1], charset='utf8')
   self._curs = self._conn.cursor()

 def close(self):
  """ Close connection, audit, remove waiting threads and also remove current threads ownership in case of nested thread ownership """
  self.count['CLOSE'] += 1
  if self._dirty:
   self.commit()
  with self._wait_lock:
   """ remove oneself and check if someone else is waiting """
   self._conn_waiting -= 1
   self._conn_in_thread -= 1
   if self._conn_waiting == 0:
    self._curs.close()
    self._conn.close()
    self._curs = None
    self._conn = None
  if self._conn_in_thread == 0:
   self._conn_lock.release()

 def query(self,aQuery, aLog = False):
  self.count['QUERY'] += 1
  if aLog:
   print("SQL: %s;"%aQuery)
  return self._curs.execute(aQuery)

 def execute(self,aQuery, aLog = False):
  self.count['EXECUTE'] += 1
  self._dirty = True
  if aLog:
   print("SQL: %s;"%aQuery)
  return self._curs.execute(aQuery)

 def commit(self):
  self.count['COMMIT'] += 1
  self._conn.commit()
  self._dirty = False

 def is_dirty(self):
  return self._dirty

 def ignore_warnings(self,aState):
  old = self._curs._defer_warnings
  self._curs._defer_warnings = aState
  return old

 ################# Fetch info ##################

 def get_row(self):
  return self._curs.fetchone()

 # Bug in fetchall, a tuple is not an empty list in contrary to func spec
 def get_rows(self):
  rows = self._curs.fetchall()
  return rows if rows != () else []

 def get_dict(self, aTarget):
  return { row[aTarget]: row for row in self._curs.fetchall() }

 def get_val(self, aTarget):
  return self._curs.fetchone().get(aTarget)

 def get_last_id(self):
  return self._curs.lastrowid

 ################# Extras ##################
 #
 def update_dict(self, aTable, aDict, aCondition = "TRUE"):
  self._dirty = True
  return self._curs.execute("UPDATE %s SET %s WHERE %s"%(aTable,",".join("%s=%s"%(k,"'%s'"%v if not (v == 'NULL' or v is None) else 'NULL') for k,v in aDict.items()),aCondition))

 def insert_dict(self, aTable, aDict, aException = ""):
  self._dirty = True
  return self._curs.execute("INSERT INTO %s(%s) VALUES(%s) %s"%(aTable,",".join(list(aDict.keys())),",".join("'%s'"%v if not (v == 'NULL' or v is None) else 'NULL' for v in aDict.values()),aException))

####################################### SNMP #########################################
#
class SnmpException(Exception):
 pass

class VarBind(object):
 """ Match the model from netsnmp - at least (!) tag and iid should be supplied """
 def __init__(self, tag=None, iid=None, val=None, type=None):
  self.tag = tag
  self.iid = iid
  self.val = val
  self.type = type
  # parse iid out of tag if needed, 'None' is not good and neither is '' for iid in client_intf
  if iid == None and tag != None:
   from re import compile
   regex = compile(r'^((?:\.\d+)+|(?:\w+(?:[-:]*\w+)+))\.?(.*)$')
   match = regex.match(tag)
   if match:
    (self.tag, self.iid) = match.group(1,2)

 def __setattr__(self, name, val):
  self.__dict__[name] = val if (name == 'val' or val == None) else str(val)

 def __str__(self):
  return "VarBind(tag=%s, iid=%s, val=%s, type=%s)"%(self.tag, self.iid, self.val, self.type)

#
#
class VarList(object):

 def __init__(self, *vs):
  """ If regular vars - i.e. strings are passed, wrap into a VarBind. This is the most common usage for Varlists """
  self.varbinds = list(var if isinstance(var, VarBind) else VarBind(var) for var in vs)

 def __len__(self):
  return len(self.varbinds)

 def __getitem__(self, index):
  return self.varbinds[index]

 def __setitem__(self, index, val):
  if isinstance(val, VarBind):
   self.varbinds[index] = val
  else:
   raise TypeError

 def __iter__(self):
  return iter(self.varbinds)

 def __delitem__(self, index):
  del self.varbinds[index]

 def __repr__(self):
  return repr(self.varbinds)

 def __getslice__(self, i, j):
  return self.varbinds[i:j]

 def append(self, *vars):
  for var in vars:
   if isinstance(var, VarBind):
    self.varbinds.append(var)
   else:
    raise TypeError

#
#
class Session(object):

 def __init__(self, **args):
  # client_intf is compiled from https://github.com/bluecmd/python3-netsnmp
  # or downloaded using pip3 python3-netsnmp...
  # TODO: find PyPy3 compatible package or solution
  from netsnmp import client_intf
  self._libmod = client_intf
  self.sess_ptr = None
  self.UseLongNames = 0
  self.UseNumeric = 0
  self.UseSprintValue = 0
  self.UseEnums = 0
  self.BestGuess = 0
  self.RetryNoSuch = 0
  self.ErrorStr = ''
  self.ErrorNum = 0
  self.ErrorInd = 0
  secLevelMap = { 'noAuthNoPriv':1, 'authNoPriv':2, 'authPriv':3 }
  sess_args = {
   'Version':3,
   'DestHost':'localhost',
   'Community':'public',
   'Timeout':1000000,
   'Retries':3,
   'RemotePort':161,
   'LocalPort':0,
   'SecLevel':'noAuthNoPriv',
   'SecName':'initial',
   'PrivProto':'DEFAULT',
   'PrivPass':'',
   'AuthProto':'DEFAULT',
   'AuthPass':'',
   'ContextEngineId':'',
   'SecEngineId':'',
   'Context':'',
   'Engineboots':0,
   'Enginetime':0,
   'UseNumeric':0,
   'OurIdentity':'',
   'TheirIdentity':'',
   'TheirHostname':'',
   'TrustCert':''
   }
  sess_args.update(args)
  sess_args['SecLevel'] = secLevelMap[sess_args['SecLevel']]
  for k,v in sess_args.items():
   self.__dict__[k] = v

  # check for transports that may be tunneled
  trans = sess_args['DestHost']

  def args2tuple(aList):
   return tuple(sess_args[x] for x in aList)

  try:
   if sess_args['Version'] < 3:
    self.sess_ptr = self._libmod.session(*args2tuple(['Version','Community','DestHost','LocalPort','Retries','Timeout']))
   elif (trans.startswith('tls') or trans.startswith('dtls') or trans.startswith('ssh')):
    self.sess_ptr = self._libmod.session_tunneled(*args2tuple(['Version','DestHost','LocalPort','Retries','Timeout','SecName','SecLevel','ContextEngineId','Context','OurIdentity','TheirIdentity','TheirHostname','TrustCert']))
   else:
    self.sess_ptr = self._libmod.session_v3(*args2tuple(['Version','DestHost','LocalPort','Retries','Timeout','SecName','SecLevel','SecEngineId','ContextEngineId','Context','AuthProto','AuthPass','PrivProto','Engineboots','Enginetime']))
  except self._libmod.Error as e:
   err = e.args[0].strip()
   if err[0] == '(' and err[-1] == ')':
    err = err[1:-1]
  else:
   err = None

  # Re-wrap the error into a pure Python class to allow it to be pickled
  # and other things. To not have the original exception attached, save
  # only the string value of the exception.
  if err:
   raise SnmpException(err)

 def oid(self,aOid):
  tmp_var = VarBind(aOid,'')
  self._libmod.get(self, VarList(tmp_var))
  return tmp_var

 def get(self, varlist):
  return self._libmod.get(self, varlist)

 def set(self, varlist):
  return self._libmod.set(self, varlist)

 def getnext(self, varlist):
  return self._libmod.getnext(self, varlist)

 def getbulk(self, nonrepeaters, maxrepetitions, varlist):
  return None if self.Version == 1 else self._libmod.getbulk(self, nonrepeaters, maxrepetitions, varlist)

 def walk(self, varlist):
  return self._libmod.walk(self, varlist)

 def __del__(self):
  try: return self._libmod.delete_session(self)
  except SystemError as e:
   print("RIMS_SNMP_ERROR: %s"%repr(e))
   return None
