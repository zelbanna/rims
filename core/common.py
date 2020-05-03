"""Common functions module """
__author__ = "Zacharias El Banna"

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

############################################ Wheel of Time scheduler ######################################
#
# Single-thread scheduler for events happening withing X seconds or every X second. Uses RIMS QueueWorker for execution to get resource control
#
# Uses:
# - Abort (Event) as a mean "stop the clock"
# - Queue which exposes a put method to add event task to be executed (avoiding introducing delay deue to execution)
# - Drift which optionally adjust clock every X:t minute. For smarter systems this should be self adjusting depending on accuracy of clock
#
class WoT(Thread):

 def __init__(self, aAbort, aQueue, aDrift = None):
  """
  Init scheduler thread, clock is [MM:ss] as events scheduled to run after an hour are put in a regular list.
  - Every minute events for that minute is distributed into the right seconds
  - Every second events scheduled to be executed are executed
  - Two lists for event execution this function ~O(1) with good memory efficiency
  """
  Thread.__init__(self)
  self._abort = aAbort
  self._queue = aQueue
  self._drift = aDrift
  self._clock = [0,0]
  self._second = [None] * 60
  self._minute = [None] * 60
  for k in range(60):
   self._second[k] = []
   self._minute[k] = []
  self._rest = []
  self.daemon = True

 def __map_time(self, aEvent, aDelay):
  """ Internal function to map an event with delay to a certain position int the event queue """
  occur = self._clock[1] * 60 + self._clock[0] + aDelay
  if occur < 3600:
   s,m = occur%60, int(occur/60)
   if m != self._clock[1]:
    aEvent['seconds'] = s
    self._minute[m].append(aEvent)
   else:
    self._second[s].append(aEvent)
  else:
   aEvent['seconds'] = occur - 3600
   self._rest.append(aEvent)

 def __tick(self):
  """
  Tick the clock one (1) second and every 60th second (possibly) reshuffle some events into the right queue.
  Function returns the scheduled events for the 'ticked clock'
  """
  self._clock[0] = (self._clock[0] + 1) % 60

  if self._clock[0] == 0:
   self._clock[1] = (self._clock[1] + 1) % 60
   if self._clock[1] == 0:
    for e in self._rest:
     if e['seconds'] < 3600:
      s,m = e['seconds']%60, int(e['seconds']/60)
      e['seconds'] = max(0,s-self._clock[0])
      self._minute[m].append(e)
     else:
      e['seconds'] -= 3600
   for e in self._minute[self._clock[1]]:
    self._second[e['seconds']].append(e)

  events = self._second[self._clock[0]]
  if len(events) > 0:
   self._second[self._clock[0]] = []
   for e in events:
    if e.get('frequency',0) > 0:
     self.__map_time(e,e['frequency'])
  return events

 ########################### Exposed methods #########################
 def events(self):
  events = []
  events.extend(e for sublist in self._second for e in sublist if e)
  events.extend(e for sublist in self._minute for e in sublist if e)
  events.extend(self._rest)
  return events

 def periodic_delay(self, aFrequency):
  """ Function gives a basic estimate on when to start for periodic functions.. when they fit  """
  return (60 - self._clock[0]) if aFrequency <= 60 else (aFrequency - int(time())%aFrequency)

 def clock(self):
  return {'minutes':self._clock[1],'seconds':self._clock[0]}

 def adjust(self):
  now = int(time())%3600
  ticks = now - (self._clock[1]*60 + self._clock[0])
  ret = ticks if ticks > 0 else (3600 + ticks)
  self._clock = [now%60,int(now/60)]
  return ret

 def fast_forward(self, aTicks):
  events = []
  for i in range(aTicks):
   events.extend(self.__tick())
  for e in events:
   self._queue.put(e['task'])

 def add_delayed(self, aTask, aName, aDelay, aFrequency = 0):
  """ Insert at 'aDelay' seconds from now with frequency 'aFrequency' """
  self.__map_time({'task':aTask, 'name':aName, 'frequency':aFrequency,'seconds':0},aDelay if aDelay > 0 else aFrequency)

 def add_periodic(self, aTask, aName, aFrequency):
  self.__map_time({'task':aTask, 'name':aName, 'frequency':aFrequency,'seconds':0},self.periodic_delay(aFrequency))

 ################################## Thread run ################################
 #
 # - Tries to start as close as possible to a second, then sleep
 # - start loop by ticking a second (because first sleep already happened)
 # - every 1 seconds a tick is performed and events are retrieved for that time
 # - sleeps roughly 1 second in each loop
 # - adjust sleep every X minute to accommodate drift/execution time
 #
 def run(self):
  abort = self._abort
  fclock = time()
  iclock = int(fclock)
  now = iclock%3600
  self._clock = [now%60,int(now/60)]
  sleeptime = (iclock + 1 - fclock)
  while not abort.is_set():
   sleep(sleeptime)
   sleeptime = 1
   events = self.__tick()
   if (self._clock[0] == 41 and self._drift and self._clock[1] % self._drift == 0):
    """ Adjust sleep here every X:th minute to avoid drifting, assume positive drift and less than a minute drifting... """
    fclock = time()
    iclock = int(fclock)
    sleeptime = (iclock + 1 - fclock)
    """ Because we know the time we can adjust clock and extend events with those that passed while we drifted, there is a caveat around every HH:00:00 """
    now = iclock%3600
    while (now > (self._clock[1] * 60 + self._clock[0])):
     events.extend(self.__tick())
   for e in events:
    self._queue.put(e['task'])
  return False

######################################## Scheduler ######################################
#
# Single-thread scheduler for events happening withing X seconds or every X second. Uses RIMS QueueWorker for execution to maintain resource control
#
# Uses:
# - Abort (Event) as a mean to "stop the clock"
# - Queue which exposes a put method to add event task to be executed (avoiding introducing delay deue to execution)
# - Drift which optionally adjust clock every X:t minute. For smarter systems this should be self adjusting depending on accuracy of clock
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
  self._queue.put(aEvent['task'])
  # print("Scheduler executing: %s"%aEvent['name'])
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
  s._internal.cancel(s._internal.queue[aKey])

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
  self.count = {'DO':0,'COMMIT':0,'CONNECT':0,'CLOSE':0}

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

 def do(self,aQuery, aLog = False):
  op = aQuery[0:6].upper()
  self.count['DO'] += 1
  self._dirty = (self._dirty or op in ['UPDATE','INSERT','DELETE'])
  if aLog:
   print("SQL: %s"%aQuery)
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
  self.count['DO'] += 1
  self._dirty = True
  return self._curs.execute("UPDATE %s SET %s WHERE %s"%(aTable,",".join("%s=%s"%(k,"'%s'"%v if not (v == 'NULL' or v is None) else 'NULL') for k,v in aDict.items()),aCondition))

 def insert_dict(self, aTable, aDict, aException = ""):
  self.count['DO'] += 1
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
