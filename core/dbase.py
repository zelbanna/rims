"""Module docstring.

DB

"""
__author__ = "Zacharias El Banna"
__version__ = "17.10.4"
__status__ = "Production"

############################################ Database ######################################
#
# Database Class
#
class DB(object):

 def __init__(self, aDB = None, aHost = None, aUser = None, aPass = None):
  self._conn = None
  self._curs = None
  if not aDB:
   import sdcp.PackageContainer as PC
   self._db, self._host, self._user, self._pass = PC.generic['db'],'localhost',PC.generic['dbuser'],PC.generic['dbpass']
  else:
   self._db, self._host, self._user, self._pass = aDB, aHost, aUser, aPass

 def __enter__(self):
  self.connect()
  return self

 def __exit__(self, ctx_type, ctx_value, ctx_traceback):
  self._curs.close()
  self._conn.close()

 def connect(self):
  from pymysql import connect
  from pymysql.cursors import DictCursor
  self._conn = connect(host=self._host, port=3306, user=self._user, passwd=self._pass, db=self._db, cursorclass=DictCursor)
  self._curs = self._conn.cursor()

 def close(self):
  self._curs.close()
  self._conn.close()

 def do(self,aStr):
  return self._curs.execute(aStr)

 def commit(self):
  self._conn.commit()

 def get_row(self):
  return self._curs.fetchone()

 # Bug in fetchall, a tuple is not an empty list in contrary to func spec
 def get_rows(self):
  rows = self._curs.fetchall()
  return rows if rows != () else []

 def get_all_dict(self, aTarget):
  return dict(map(lambda x: (x[aTarget],x),self._curs.fetchall()))

 def get_cursor(self):
  return self._curs

 def get_last_id(self):
  return self._curs.lastrowid
