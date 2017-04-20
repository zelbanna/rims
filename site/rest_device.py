"""Module docstring.

 Device restAPI module

"""
__author__ = "Zacharias El Banna"                     
__version__ = "10.5GA"
__status__ = "Production"

#
# Dump 2 JSON              
#
def dump_db(aDict):
 import sdcp.core.GenLib as GL
 db = GL.DB()
 db.connect()
 res = db.do("SELECT * FROM devices")
 db.close()
 if res > 0:
  return db.get_all_rows()
 else:
  return []
