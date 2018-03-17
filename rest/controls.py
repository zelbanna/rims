"""Controls API module. Provides generic control functionality"""
__author__ = "Zacharias El Banna"
__version__ = "18.03.16GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)


def list(aDict):
 """Function docstring for list TBD

 Args:

 Output:
 """
 ret = {}
 with DB() as db:
  ret['xist'] = db.do("SELECT id, alias, name, email FROM users ORDER by name")
  ret['data'] = db.get_rows()
 return ret
