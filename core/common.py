"""Module docstring.

DB module

"""
__author__ = "Zacharias El Banna"
__version__ = "18.03.07GA"
__status__ = "Production"


try:    from .. import SettingsContainer as SC
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
   self._db, self._host, self._user, self._pass = SC.system['db_name'],SC.system['db_host'],SC.system['db_user'],SC.system['db_pass']
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
  self._conn = connect(host=self._host, port=3306, user=self._user, passwd=self._pass, db=self._db, cursorclass=DictCursor)
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
  """Assumes not inserting NULL"""
  self._dirty = True
  return "INSERT INTO %s(%s) VALUES('%s') %s"%(aTable,",".join(args.keys()),"','".join(args.values()),aException)
