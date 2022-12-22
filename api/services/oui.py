"""OUI API module. Implements OUI sync logic"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "INFO"

from urllib.request import urlopen, Request
from urllib.error import HTTPError

#
#
def list(aRT, aArgs):
 """Function returns a list of OUI:s

 Args:

 Output:
  - data
 """
 ret = {}
 with aRT.db as db:
  db.query("SELECT LPAD(HEX(oui),6,0) AS oui, company FROM oui")
  ret['data'] = db.get_rows()
 return ret

def info(aRT, aArgs):
 """ Function retrieves OUI info from database

 Args:
  - oui (required). string, e.g. "AABB00"

 Output:
  - status
  - data
 """
 ret = {}
 try:
  oui = int(aArgs['oui'].translate(str.maketrans({":":"","-":""}))[:6],16)
  with aRT.db as db:
   ret['data']= db.get_row() if db.query("SELECT LPAD(HEX(oui),6,0) AS oui, company FROM oui WHERE oui = %s"%oui) else {'oui':'NOT_FOUND','company':'NOT_FOUND'}
   ret['status'] = 'OK' if ret['data']['oui'] != 'NOT_FOUND' else 'NOT_FOUND'
 except Exception as e:
  ret = {'status':'NOT_OK','info':repr(e),'data':{'oui':None,'company':''}}
 return ret

#########################################################################3
#
#
def status(aRT, aArgs):
 """Function docstring for status. No OP

 Args:
  - type (required)

 Output:
  - data
 """
 return {'data':None, 'status':'OK' }

#
#
def sync(aRT, aArgs):
 """ Function fetch and populate OUI table

 Args:
  - id (required). Server id on master node
  - clear (optional). Bool. Clear database before populating if true. Defaults to false


 Output:
  - code. (error code, optional)
  - output. (output from command)
  - status. (operation result)
 """
 ret = {'output':0,'status':'NOT_OK'}
 try:
  req = Request(aRT.config['services']['oui']['location'])
  sock = urlopen(req, timeout = 120)
  data = sock.read().decode()
  sock.close()
 except HTTPError as h:
  ret.update({'status':'HTTPError', 'code':h.code, 'info':dict(h.info())})
 except Exception as e:
  ret.update({ 'status':type(e).__name__, 'code':590, 'error':repr(e)})
 else:
  with aRT.db as db:
   if aArgs.get('clear') is True:
    db.execute("TRUNCATE oui")
   for line in data.split('\n'):
    if line:
     parts = line.split()
     if len(parts) > 3 and parts[1] == '(base' and parts[2] == '16)':
      oui = int(parts[0].upper(),16)
      company = (" ".join(parts[3:]).replace("'",''))[0:60]
      ret['output'] += db.execute("INSERT INTO oui(oui,company) VALUES(%d,'%s') ON DUPLICATE KEY UPDATE company = '%s'"%(oui,company,company))
   ret['status'] = 'OK'
 return ret

#
#
def restart(aRT, aArgs):
 """Function provides restart capabilities of service

 Args:

 Output:
  - code
  - output
  - result 'OK'/'NOT_OK'
 """
 return {'status':'OK','code':0,'output':""}

#
#
def parameters(aRT, aArgs):
 """ Function provides parameter mapping of anticipated config vs actual

 Args:

 Output:
  - status
  - parameters
 """
 settings = aRT.config['services'].get('oui',{})
 params = ['location']
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}

#
#
def start(aRT, aArgs):
 """ Function provides start behavior

 Args:

 Output:
  - status
 """
 return {'status':'NO OP'}

#
#
def stop(aRT, aArgs):
 """ Function provides stop behavior

 Args:

 Output:
  - status
 """
 return {'status':'NO OP'}

#
#
def close(aRT, aArgs):
 """ Function provides closing behavior, wrapping up data and file handlers before closing

 Args:

 Output:
  - status
 """
 return {'status':'NO OP'}
