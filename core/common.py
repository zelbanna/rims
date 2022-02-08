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
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.domain.write_precision import WritePrecision

########################################### REST ##########################################
#
# Rest with exception and variable args handling to make it more robust and streamlined in a "one-liner"
#
#
def basic_auth(aUsername,aPassword):
 return {'Authorization':'Basic %s'%(b64encode(f"{aUsername}:{aPassword}".encode('utf-8')).decode('utf-8')) }

class RestException(Exception):

 def __init__(self, *args):
  self.code = args[0]
  self.exception = args[1]
  self.info = args[2]
  self.data = args[3]

 def __str__(self):
  return f"REST({self.code}): {self.exception} => {self.data}"

def rest_call(aURL, **kwargs):
 """ REST call function, aURL is required, then aApplication (default:'json' or 'x-www-form-urlencoded'), aArgs, aHeader (dict), aTimeout, aDataOnly (default True), aDecode (not for binary..) . Returns de-json:ed data structure and all status codes """
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
  if kwargs.get('aVerify',True):
   sock = urlopen(req, timeout = kwargs.get('aTimeout',20))
  else:
   ssl_ctx = create_default_context()
   ssl_ctx.check_hostname = False
   ssl_ctx.verify_mode = CERT_NONE
   sock = urlopen(req,context=ssl_ctx, timeout = kwargs.get('aTimeout',20))
  try:
   data = loads(sock.read().decode()) if kwargs.get('aDecode',True) else sock.read()
  except:
   data = None
  res = data if kwargs.get('aDataOnly',True) else {'info':dict(sock.info()), 'code':sock.code, 'data':data }
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

######################################## InfluxDB ######################################
#
# InfluxDB 2.x compatible handler
# Add a default Handler
class InfluxDB():

 def __init__(self, aUrl, aOrg, aToken, aBucket = None):
  self.url = aUrl
  self.org = aOrg
  self.token = aToken
  self.bucket = aBucket
  self.client = InfluxDBClient(url=aUrl, token=aToken, org=aOrg)
  self.precision = WritePrecision.S
  self.write_mode = SYNCHRONOUS

 def status(self, aCTX, aArgs):
  try:
   return self.ic.health().to_dict()
  except Exception as e:
   return str(e)

 def query_csv(self, aQuery, aDialect = None):
  return self.client.query_api().query_csv(dialect = {'annotations': ['default'], 'comment_prefix': '#', 'date_time_format': 'RFC3339', 'delimiter': ',', 'header': True} if not aDialect else aDialect, query = aQuery)

 def write(self, aRecords, aBucket = None):
  try:
   bucket = aBucket if aBucket else self.bucket
   with self.client.write_api(write_options=self.write_mode) as write_api:
    write_api.write(bucket = bucket, write_precision = self.precision, record = aRecords)
  except Exception as e:
   raise Exception(e)
  else:
   return True


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
   print(f"SQL: {aQuery}")
  self.count['QUERY'] += 1
  return self._curs.execute(aQuery)

 def execute(self,aQuery, aPrint = False):
  if aPrint:
   print(f"SQL: {aQuery}")
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

####################################### SNMP #########################################
#
class SnmpException(Exception):
 pass

class VarBind():
 """ Match the model from netsnmp - at least (!) tag and iid should be supplied """

 def __init__(self, tag=None, iid=None, val=None, tp=None):
  self.tag = tag
  self.iid = iid
  self.val = val
  self.type = tp
  # parse iid out of tag if needed, 'None' is not good and neither is '' for iid in client_intf
  if iid is None and tag is not None:
   from re import compile as re_compile
   regex = re_compile(r'^((?:\.\d+)+|(?:\w+(?:[-:]*\w+)+))\.?(.*)$')
   match = regex.match(tag)
   if match:
    (self.tag, self.iid) = match.group(1,2)

 def __setattr__(self, name, val):
  self.__dict__[name] = val if (name == 'val' or val is None) else str(val)

 def __str__(self):
  return f"VarBind(tag={self.tag}, iid={self.iid}, val={self.val}, type={self.type})"

#
#
class VarList():

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

 def append(self, *vrs):
  for var in vrs:
   if isinstance(var, VarBind):
    self.varbinds.append(var)
   else:
    raise TypeError

#
#
class Session():

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
  try:
   return self._libmod.delete_session(self)
  except SystemError as e:
   stderr.write(f"RIMS_SNMP_ERROR: {e}")
   return None
