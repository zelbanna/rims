"""Module docstring.

DB module

"""
__author__ = "Zacharias El Banna"
__version__ = "1.0GA"
__status__ = "Production"

############################################ Database ######################################
#
# Basic logger
#
def log(aMsg,aID='None'):
 from zdcp.SettingsContainer import SC
 try:
  with open(SC['logs']['system'], 'a') as f:
   from time import localtime, strftime
   f.write(unicode("%s (%s): %s\n"%(strftime('%Y-%m-%d %H:%M:%S', localtime()), aID, aMsg)))
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
   from zdcp.SettingsContainer import SC
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
 #
 # Assume dict keys are prefixed by aTable and separated by a single character (e.g. _)

 def update_dict_prefixed(self, aTable, aDict, aCondition = "TRUE"):
  self._dirty = True
  key_len = len(aTable) + 1
  return self._curs.execute("UPDATE %s SET %s WHERE %s"%(aTable,",".join(["%s=%s"%(k[key_len:],"'%s'"%v if v != 'NULL' else 'NULL') for k,v in aDict.iteritems() if k.startswith(aTable)]),aCondition))

 def update_dict(self, aTable, aDict, aCondition = "TRUE"):
  self._dirty = True
  return self._curs.execute("UPDATE %s SET %s WHERE %s"%(aTable,",".join(["%s=%s"%(k,"'%s'"%v if v != 'NULL' else 'NULL') for k,v in aDict.iteritems()]),aCondition))

 def insert_dict(self, aTable, aDict, aException = ""):
  self._dirty = True
  return self._curs.execute("INSERT INTO %s(%s) VALUES(%s) %s"%(aTable,",".join(aDict.keys()),",".join(["'%s'"%v if v != 'NULL' else 'NULL' for v in aDict.values()]),aException))

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
 from zdcp.SettingsContainer import SC
 if SC['system']['id'] != aNode:
  ret = rest_call("%s/api/%s_%s"%(SC['nodes'][aNode],aModule,aFunction),aArgs)['data']
 else:
  from importlib import import_module
  module = import_module("zdcp.rest.%s"%aModule)
  fun = getattr(module,aFunction,None)
  ret = fun(aArgs if aArgs else {})
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
  log("rest_call -> %s '%s'"%(aURL,dumps(aArgs)))
  req = Request(aURL, headers = head, data = dumps(aArgs) if aArgs else None)
  if aMethod:
   req.get_method = lambda: aMethod
  if aVerify is None or aVerify is True:
   sock = urlopen(req, timeout = aTimeout)
  else:
   from ssl import _create_unverified_context
   sock = urlopen(req,context=_create_unverified_context(), timeout = aTimeout)
  output = {'info':dict(sock.info()), 'code':sock.code }
  output['node'] = output['info'].pop('x-api-node','_no_node_')
  try:    output['data'] = loads(sock.read())
  except: output['data'] = None
  if (output['info'].get('x-api-res','OK') == 'ERROR'):
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
 output['info']['x-api-code'] = code_to_string(output['code'])
 if output.get('exception'):
  raise Exception(output)
 return output

#
# Basic Auth header generator for base64 authentication
#
def basic_auth(aUsername,aPassword):
 return {'Authorization':'Basic ' + (("%s:%s"%(aUsername,aPassword)).encode('base64')).replace('\n','') }

#
# HTML Code translator
#
def code_to_string(aCode):
 return {200:'OK',201:'Created',204:'No Content',304:'Not Modified',400:'Bad Request',401:'Unauthorized',403:'Forbidden',404:'Not Found',500:'Internal Server Error',591:'Z-Exception'}.get(aCode,'%s Code Not Encoded'%aCode)
