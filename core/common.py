"""Module docstring.

DB module

"""
__author__ = "Zacharias El Banna"
__version__ = "18.04.07GA"
__status__ = "Production"


try:    from sdcp.SettingsContainer import SC
except: pass

############################################ Database ######################################
#
# Database Class
#
class DB(object):

 def __init__(self, aDB = None, aHost = None, aUser = None, aPass = None):
  self._conn = None
  self._curs = None
  self._dirty = False
  if not aDB:
   self._db, self._host, self._user, self._pass = SC['system']['db_name'],SC['system']['db_host'],SC['system']['db_user'],SC['system']['db_pass']
  else:
   self._db, self._host, self._user, self._pass = aDB, aHost, aUser, aPass

 def __enter__(self):
  self.connect()
  return self

 def __exit__(self, *ctx_info):
  self.close()

 def __str__(self):
  return "DB:{} Host:{} Uncommited:{}".format(self._db,self._host,self._dirty)

 def connect(self):
  from pymysql import connect
  from pymysql.cursors import DictCursor
  self._conn = connect(host=self._host, port=3306, user=self._user, passwd=self._pass, db=self._db, cursorclass=DictCursor, charset='utf8')
  self._curs = self._conn.cursor()

 def close(self):
  if self._dirty:
   self.commit()
  self._curs.close()
  self._conn.close()

 def do(self,aQuery):
  op = aQuery[0:6].upper()
  self._dirty = (self._dirty or op in ['UPDATE','INSERT','DELETE'])
  return self._curs.execute(aQuery)

 def commit(self):
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

 def update_dict_prefixed(self, aTable, aDict, aCondition):
  self._dirty = True
  return self._curs.execute("UPDATE %s SET %s WHERE %s"%(aTable,",".join([ key.partition('_')[2] + "=" + ("NULL" if value == 'NULL' else "'%s'"%value) for key,value in aDict.iteritems() if key.split('_')[0] == aTable]),aCondition))

 def update_dict(self, aTable, aDict, aCondition):
  self._dirty = True
  return self._curs.execute("UPDATE %s SET %s WHERE %s"%(aTable,",".join([ key + "=" + ("NULL" if value == 'NULL' else "'%s'"%value) for key,value in aDict.iteritems()]),aCondition))

 def insert_dict(self, aTable, aDict, aException = ""):
  self._dirty = True
  return self._curs.execute("INSERT INTO %s(%s) VALUES(%s) %s"%(aTable,",".join(aDict.keys()),",".join(["'%s'"%val if not val == 'NULL' else 'NULL' for val in aDict.values()]),aException))

######################################### NODE ########################################
#
#
def node_call(aNode, aModule, aFunction, aArgs = None, aMethod = None, aHeader = None, aVerify = None, aTimeout = 20):
 """ Node call function, automatically translates node call to rest call with shortcut for local node. Typical usage is REST call from within REST...

  Args:
   - aNode (required)
   - aModule (required)
   - aFunction (required)
   - aArgs (optional)
   - ... (optional)

  Output:
   - de-json:ed data structure that function returns (hence status codes etc is not available)

 """
 ret = {}
 if SC['system']['id'] == aNode:
  from importlib import import_module
  module = import_module("sdcp.rest.%s"%aModule)
  fun = getattr(module,aFunction,None)
  ret = fun(aArgs if aArgs else {})
 else:              
  ret = rest_call("%s?%s_%s"%(SC['node'][aNode],aModule,aFunction),aArgs)['data']
 return ret

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
 from urllib2 import urlopen, Request, URLError, HTTPError
 try:
  head = { 'Content-Type': 'application/json','Accept':'application/json' }
  try:    head.update(aHeader)
  except: pass
  try:    from logger import log
  except: pass
  else:   log("rest_call -> %s '%s'"%(aURL,dumps(aArgs)))
  req = Request(aURL, headers = head, data = dumps(aArgs) if aArgs else None)
  if aMethod:
   req.get_method = lambda: aMethod
  if aVerify is None or aVerify is True:
   sock = urlopen(req, timeout = aTimeout)
  else:
   from ssl import _create_unverified_context
   sock = urlopen(req,context=_create_unverified_context(), timeout = aTimeout)
  output = {'info':dict(sock.info()), 'code':sock.code }
  output['node'] = output['info'].pop('x-z-node','_no_node_')
  try:    output['data'] = loads(sock.read())
  except: output['data'] = None
  if (output['info'].get('x-z-res','OK') == 'ERROR'):
   output['info'].pop('server',None)
   output['info'].pop('connection',None)
   output['info'].pop('transfer-encoding',None)
   output['info'].pop('content-type',None)
   output['exception'] = 'RESTError'
  sock.close()
 except HTTPError as h:
  raw = h.read()
  try:    data = loads(raw)
  except: data = raw
  output = { 'result':'ERROR', 'exception':'HTTPError', 'code':h.code, 'info':dict(h.info()), 'data':data }
 except URLError as e:  output = { 'result':'ERROR', 'exception':'URLError',  'code':590, 'info':{'error':str(e)}}
 except Exception as e: output = { 'result':'ERROR', 'exception':type(e).__name__, 'code':591, 'info':{'error':str(e)}}
 if output.get('exception'):
  raise Exception(output)
 return output

#
# Basic Auth header generator for base64 authentication
#
def basic_auth(aUsername,aPassword):
 return {'Authorization':'Basic ' + (("%s:%s"%(aUsername,aPassword)).encode('base64')).replace('\n','') }
