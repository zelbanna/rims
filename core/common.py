"""Module docstring.

DB module

"""
__author__ = "Zacharias El Banna"
__version__ = "5.1GA"
__status__ = "Production"

############################################# Logger ######################################
#
# Basic logger
#
def log(aMsg,aID='None'):
 from zdcp.Settings import Settings
 try:
  with open(Settings['logs']['system'], 'a') as f:
   from time import localtime, strftime
   f.write(str("%s (%s): %s\n"%(strftime('%Y-%m-%d %H:%M:%S', localtime()), aID, aMsg)))
 except: pass

############################################ Database ######################################
#
# Database Class
#
class DB(object):

 def __init__(self, aDB = None, aHost = None, aUser = None, aPass = None):
  from threading import Lock
  from pymysql import connect
  from pymysql.cursors import DictCursor
  self._mods = (connect,DictCursor)
  self._conn, self._curs, self._dirty, self._clock, self._wlock = None, None, False, Lock(), Lock()
  self._waiting = 0
  self.count = {'SELECT':0,'INSERT':0,'DELETE':0,'UPDATE':0,'COMMIT':0,'CONNECT':0,'CLOSE':0}
  if not aDB:
   from zdcp.Settings import Settings
   self._db, self._host, self._user, self._pass = Settings['system']['db_name'],Settings['system']['db_host'],Settings['system']['db_user'],Settings['system']['db_pass']
  else:
   self._db, self._host, self._user, self._pass = aDB, aHost, aUser, aPass

 def __enter__(self):
  self.connect()
  return self

 def __exit__(self, *ctx_info):
  self.close()

 def __str__(self):
  return "Database(%s@%s):[DIRTY=%s,%s]"%(self._db,self._host,self._dirty,",".join("%s=%03d"%i for i in self.count.items()))

 def connect(self):
  with self._wlock:
   self._waiting += 1
  self._clock.acquire()
  self.count['CONNECT'] += 1
  if not self._conn:
   self._conn = self._mods[0](host=self._host, port=3306, user=self._user, passwd=self._pass, db=self._db, cursorclass=self._mods[1], charset='utf8')
   self._curs = self._conn.cursor()

 def close(self):
  self.count['CLOSE'] += 1
  if self._dirty:
   self.commit()
  with self._wlock:
   """ remove oneself and check if someone else is waiting """
   self._waiting -= 1
   if self._waiting == 0:
    self._curs.close()
    self._conn.close()
    self._curs = None
    self._conn = None
  self._clock.release()

 def do(self,aQuery):
  op = aQuery[0:6].upper()
  self.count[op] += 1
  self._dirty = (self._dirty or op in ['UPDATE','INSERT','DELETE'])
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
 # Assume dict keys are prefixed by aTable and separated by a single character (e.g. _)

 def update_dict_prefixed(self, aTable, aDict, aCondition = "TRUE"):
  self.count['UPDATE'] += 1
  self._dirty = True
  key_len = len(aTable) + 1
  return self._curs.execute("UPDATE %s SET %s WHERE %s"%(aTable,",".join("%s=%s"%(k[key_len:],"'%s'"%v if v != 'NULL' else 'NULL') for k,v in aDict.items() if k.startswith(aTable)),aCondition))

 def update_dict(self, aTable, aDict, aCondition = "TRUE"):
  self.count['UPDATE'] += 1
  self._dirty = True
  return self._curs.execute("UPDATE %s SET %s WHERE %s"%(aTable,",".join("%s=%s"%(k,"'%s'"%v if v != 'NULL' else 'NULL') for k,v in aDict.items()),aCondition))

 def insert_dict(self, aTable, aDict, aException = ""):
  self.count['INSERT'] += 1
  self._dirty = True
  return self._curs.execute("INSERT INTO %s(%s) VALUES(%s) %s"%(aTable,",".join(list(aDict.keys())),",".join("'%s'"%v if v != 'NULL' else 'NULL' for v in aDict.values()),aException))

######################################### REST ########################################
#
#
def rest_call(aURL, aArgs = None, aMethod = None, aHeader = None, aVerify = None, aTimeout = 20):
 """ Rest call function
  Args:
   - aURL (required)
   - aArgs (optional)
   - ... (optional)

  Output:
   - de-json:ed data structure that function returns and all status codes

 """
 from json import loads, dumps
 from urllib.request import urlopen, Request
 from urllib.error import HTTPError
 try:
  head = { 'Content-Type': 'application/json','Accept':'application/json' }
  try:    head.update(aHeader)
  except: pass
  if aArgs:
   data = dumps(aArgs)
   data = data.encode('utf-8')
  else:
   data = None
  req = Request(aURL, headers = head, data = data)
  if aMethod:
   req.get_method = lambda: aMethod
  if aVerify is None or aVerify is True:
   sock = urlopen(req, timeout = aTimeout)
  else:
   from ssl import _create_unverified_context
   sock = urlopen(req,context=_create_unverified_context(), timeout = aTimeout)
  output = {'info':dict(sock.info()), 'code':sock.code }
  output['node'] = output['info'].pop('node','_no_node_')
  try:    output['data'] = loads(sock.read().decode())
  except: output['data'] = None
  if (output['info'].get('code',200) != 200):
   output['info'].pop('server',None)
   output['info'].pop('connection',None)
   output['info'].pop('transfer-encoding',None)
   output['info'].pop('content-type',None)
   output['exception'] = 'RESTError'
  sock.close()
 except HTTPError as h:
  raw = h.read()
  try:    data = loads(raw.decode())
  except: data = raw
  output = { 'exception':'HTTPError', 'code':h.code, 'info':dict(h.info()), 'data':data }
 except Exception as e: output = { 'exception':type(e).__name__, 'code':590, 'info':{'error':str(e)}}
 if output.get('exception'):
  raise Exception(output)
 return output
