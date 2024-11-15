"""Common functions module """
__author__ = "Zacharias El Banna"

from sys import stderr
from base64 import b64encode
from json import loads, dumps
from sched import scheduler
from threading import Thread, Lock, RLock, Event
from time import time, sleep
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
 return {'Authorization':'Basic %s'%(b64encode(f"{aUsername}:{aPassword}".encode('utf-8')).decode('utf-8')) }

#
class RestException(Exception):

 def __init__(self, *args):
  self.code = args[0]
  self.exception = args[1]
  self.info = args[2]
  self.data = args[3]

 def __str__(self):
  return f"REST({self.code}): {self.exception} => {self.data}"

#
def ssl_context():
 ssl_ctx = create_default_context()
 ssl_ctx.check_hostname = False
 ssl_ctx.verify_mode = CERT_NONE
 return ssl_ctx

#
def rest_call(aURL, **kwargs):
 """ REST call function, aURL is required, then aApplication (default:'json' or 'x-www-form-urlencoded'), aArgs, aHeader (dict), aSSL (default 'None),  aTimeout, aDebug (default False), aDecode (not for binary..) . Returns de-json:ed data structure and all status codes """
 try:
  head = { 'Content-Type': f"application/{kwargs.get('aApplication','json')}",'Accept':'application/json' }
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
   raise RestException(f"No recognized application type ({head['Content-Type']})")
  req = Request(aURL, headers = head, data = args)
  req.get_method = lambda: kwargs.get('aMethod','POST')
  sock = urlopen(req, context = kwargs.get('aSSL',None), timeout = kwargs.get('aTimeout',20))
  try:
   data = loads(sock.read().decode()) if kwargs.get('aDecode',True) else sock.read()
  except:
   data = None
  res = data if not kwargs.get('aDebug',False) else {'info':dict(sock.info()), 'code':sock.code, 'data':data }
  sock.close()
 except HTTPError as h:
  ecode, etype, einfo = h.code, 'HTTPError', dict(h.info())
  try:
   edata = loads(h.read().decode())
  except:
   edata = None
 except Exception as e:
  ecode, etype, einfo, edata = 600, type(e).__name__, {'exception_error':repr(e)}, None
 else:
  ecode = None
 if ecode:
  raise RestException(ecode,etype,einfo,edata)
 return res

######################################## InfluxDB Class ######################################
#
# InfluxDB 2.x compatible handler
# Add a default Handler
class InfluxDB():

 def __init__(self, aUrl, aOrg, aToken, aBucket = None):
  # place import here to avoid import if influxdb is not necessary
  from influxdb_client import InfluxDBClient
  from influxdb_client.client.write_api import SYNCHRONOUS
  from influxdb_client.domain.write_precision import WritePrecision
  self._url = aUrl
  self._org = aOrg
  self._token = aToken
  self._bucket = aBucket
  self._client = InfluxDBClient(url=aUrl, token=aToken, org=aOrg)
  self._precision = WritePrecision.S
  self._write_mode = SYNCHRONOUS
  self._buckets = {}
  self._active = True
  self._lock = Lock()

 #
 def close(self):
  self._active = False

 #
 def status(self):
  try:
   return self._client.health().to_dict()
  except Exception as e:
   return str(e)

 #
 def buffer(self):
  size = 0
  for v in self._buckets.values():
   size += len(v)
  return size

 #
 def active(self,aState = None):
  if aState is None:
   return self._active
  with self._lock:
   self._active = aState

 # Synchronizes writes against DB
 def sync(self):
  if not self._active:
   return False
  with self._lock:
   try:
    with self._client.write_api(write_options=self._write_mode) as write_api:
     for k,l in self._buckets.items():
      for g in l:
       if self._active:
        write_api.write(bucket = k, write_precision = self._precision, record = g)
   except Exception as e:
    raise Exception(e)
   finally:
    self._buckets = {}
  return True

 #
 def query(self, aQuery):
  return self._client.query_api().query(org=self._org, query = query)

 #
 def write(self, aRecords, aBucket = None):
  if not self._active:
   return False
  with self._lock:
   bucket_id = self._bucket if not aBucket else aBucket
   bucket = self._buckets.get(bucket_id)
   if not bucket:
    self._buckets[bucket_id] = [aRecords]
   else:
    bucket.append(aRecords)
  return True

##### Dummy class #####

class InfluxDummy():

 def __init__(self):
  pass

 def status(self):
  return "InfluxDB Dummy"

 def buffer(self):
  return 0

 def close(self):
  pass

 def active(self, aState = None):
  return False

 def sync(self):
  return True

 def write(self, aRecords, aBucket = None):
  return False

######################################## Scheduler ######################################
#
# Single-thread scheduler for events happening withing X seconds or every X second. Uses RIMS Worker for execution to maintain resource control
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

 @staticmethod
 def periodic_delay(aFrequency):
  """ Function gives a basic estimate on when to start for periodic functions.. when they fit """
  return aFrequency - int(time())%aFrequency

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
class DB():

 def __init__(self, aDB, aHost, aUser, aPass):
  from pymysql import connect
  from pymysql.cursors import DictCursor
  self._mods = (connect,DictCursor)
  self._db, self._host, self._user, self._pass = aDB, aHost, aUser, aPass
  self._conn, self._curs, self._dirty = None, None, False
  self._conn_lock, self._wait_lock = RLock(), Lock()
  self._conn_waiting = 0
  self.count = {'COMMIT':0,'CONNECT':0,'CLOSE':0,'QUERY':0,'EXECUTE':0}

 def __enter__(self):
  self.connect()
  return self

 def __exit__(self, *ctx_info):
  self.close()

 def connect(self):
  """ Connect and acquire a connection lock once"""
  with self._wait_lock:
   self._conn_waiting += 1
  self._conn_lock.acquire()
  self.count['CONNECT'] += 1
  if not self._conn:
   self._conn = self._mods[0](host=self._host, port=3306, user=self._user, passwd=self._pass, db=self._db, cursorclass=self._mods[1], charset='utf8')
   self._curs = self._conn.cursor()

 def close(self):
  """ Close connection, audit, remove waiting threads and also decrease reentrant lock once"""
  self.count['CLOSE'] += 1
  if self._dirty:
   self.commit()
  with self._wait_lock:
   # remove oneself and check if someone else is waiting
   self._conn_waiting -= 1
   if not self._conn_waiting:
    self._curs.close()
    self._conn.close()
    self._curs = None
    self._conn = None
  # Call release once - with every close - to match every 'acquire' and to keep lock correct (!)
  self._conn_lock.release()

 def query(self,aQuery, aPrint = False):
  if aPrint:
   stderr.write(f"SQL: {aQuery}\n")
  self.count['QUERY'] += 1
  return self._curs.execute(aQuery)

 def execute(self,aQuery, aPrint = False):
  if aPrint:
   stderr.write(f"SQL: {aQuery}\n")
  self.count['EXECUTE'] += 1
  self._dirty = True
  return self._curs.execute(aQuery)

 def commit(self):
  self.count['COMMIT'] += 1
  self._conn.commit()
  self._dirty = False

 def is_dirty(self):
  return self._dirty

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
  self.count['EXECUTE'] += 1
  return self._curs.execute(f"UPDATE {aTable} SET %s WHERE {aCondition}"%','.join(f"{k}='{v}'" if v not in ['NULL',None] else f"{k}=NULL" for k,v in aDict.items()))

 def insert_dict(self, aTable, aDict, aException = ""):
  self._dirty = True
  self.count['EXECUTE'] += 1
  return self._curs.execute(f"INSERT INTO {aTable}({','.join(list(aDict.keys()))}) VALUES (%s) {aException}"%','.join(f"'{v}'" if v not in ['NULL',None] else 'NULL' for v in aDict.values()))
