"""Module docstring.

DB module

- also exports PC for dbase settings

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"


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
   from sdcp import PackageContainer as PC
   self._db, self._host, self._user, self._pass = PC.generic['db'],'localhost',PC.generic['dbuser'],PC.generic['dbpass']
  else:
   self._db, self._host, self._user, self._pass = aDB, aHost, aUser, aPass

 def __enter__(self):
  self.connect()
  return self

 def __exit__(self, *ctx_info):
  if self._dirty:
   self.commit()
  self.close()

 def __str__(self):
  return "DB:{} Host:{} Uncommited:{}".format(self._db,self._host,self._dirty)

 def connect(self):
  from pymysql import connect
  from pymysql.cursors import DictCursor
  self._conn = connect(host=self._host, port=3306, user=self._user, passwd=self._pass, db=self._db, cursorclass=DictCursor)
  self._curs = self._conn.cursor()

 def close(self):
  self._curs.close()
  self._conn.close()

 def do(self,aQuery):
  op = aQuery[0:6].upper()
  self._dirty = (self._dirty or op == 'UPDATE' or op == 'INSERT' or op == 'DELETE')
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

 @classmethod
 def dict2string(cls, aDict):
  return ", ".join(["%s='%s'"%(key,value) for key,value in aDict.iteritems()])
