"""Common module, i.e. database, log, rest_call and SNMP functions"""
__author__ = "Zacharias El Banna"

############################################ Database ######################################
#
# Threads safe Database Class
# - Current Thread can reenter (RLook)
# - Other Threads will wait for resource
#
class DB(object):

 def __init__(self, aDB, aHost, aUser, aPass):
  from threading import Lock, RLock
  from pymysql import connect
  from pymysql.cursors import DictCursor
  self._mods = (connect,DictCursor)
  self._db, self._host, self._user, self._pass = aDB, aHost, aUser, aPass
  self._conn, self._curs, self._dirty = None, None, False
  self._conn_lock, self._wait_lock = RLock(), Lock()
  self._conn_waiting = 0
  self._conn_in_thread = 0
  self.count = {'SELECT':0,'INSERT':0,'DELETE':0,'UPDATE':0,'COMMIT':0,'CONNECT':0,'CLOSE':0,'TRUNCA':0}

 def __enter__(self):
  self.connect()
  return self

 def __exit__(self, *ctx_info):
  self.close()

 def __str__(self):
  return "Database(%s@%s):[DIRTY=%s,%s]"%(self._db,self._host,self._dirty,",".join("%s=%03d"%i for i in self.count.items()))

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
class RestException(Exception):
 pass

from json import loads, dumps
from urllib.request import urlopen, Request
from urllib.error import HTTPError

def rest_call(aURL, **kwargs):
 """ Rest call function
  Args:
   - aURL (required)
   - aArgs (optional)
   - ... (optional)

  Output:
   - de-json:ed data structure that function returns and all status codes

 """
 try:
  head = { 'Content-Type': 'application/json','Accept':'application/json' }
  try:    head.update(kwargs.get('aHeader',{}))
  except: pass
  data = dumps(kwargs['aArgs']).encode('utf-8') if kwargs.get('aArgs') else None
  req = Request(aURL, headers = head, data = data)
  if kwargs.get('aMethod'):
   req.get_method = lambda: kwargs['aMethod']
  if kwargs.get('aVerify',True):
   sock = urlopen(req, timeout = kwargs.get('aTimeout',20))
  else:
   from ssl import create_default_context
   ssl_ctx = ssl.create_default_context()
   ssl_ctx.check_hostname = False
   ssl_ctx.verify_mode = ssl.CERT_NONE
   sock = urlopen(req,context=ssl_ctx, timeout = aTimeout)
  output = {'info':dict(sock.info()), 'code':sock.code }
  output['node'] = output['info'].pop('node','_no_node_')
  try:    output['data'] = loads(sock.read().decode()) if kwargs.get('aDecode',True) else sock.read()
  except: output['data'] = None
  if (output['info'].get('code',200) != 200):
   output['code'] = output['info']['code']
   output['exception'] = 'RESTError'
  sock.close()
 except HTTPError as h:
  output = { 'exception':'HTTPError', 'code':h.code, 'info':dict(h.info())}
  try:    output['data'] = loads(h.read().decode())
  except: pass
 except Exception as e: output = { 'exception':type(e).__name__, 'code':590, 'info':{'error':repr(e)}}
 if output.get('exception'):
  raise RestException(output)
 return output

####################################### SNMP #########################################
#
class SnmpException(Exception):
 pass

class Varbind(object):
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
  return "Varbind(%s,%s,%s,%s)"%(self.tag, self.iid, self.val, self.type)

#
#
class VarList(object):

 def __init__(self, *vs):
  self.varbinds = list(var if isinstance(var, Varbind) else Varbind(var) for var in vs)

 def __len__(self):
  return len(self.varbinds)

 def __getitem__(self, index):
  return self.varbinds[index]

 def __setitem__(self, index, val):
  if isinstance(val, Varbind):
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
   if isinstance(var, Varbind):
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
  tmp_var = Varbind(aOid,'')
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
  return self._libmod.delete_session(self)
