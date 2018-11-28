"""Logger module. Provides a service interface towards log facility

Settings under section 'logger':

- log: parameter value from logs (! this means reuse of an existing log file)

"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "NOTIFY"

#
#
def status(aCTX, aArgs = None):
 """Function returns settings for logger

 Args:

 Output:
 """
 ret = {'settings':aCTX.settings.get('logger',{})}
 if aCTX.settings.get('logger'):
  try:
   lines = ["\r" for i in range(10)]
   pos = 0
   with open(aCTX.settings['logs'][aCTX.settings['logger']['log']],'r') as f:
    for line in f:
     lines[pos] = line
     pos = (pos + 1) % 10
    ret['log'] = [lines[(pos + n) % 10][:-1] for n in reversed(list(range(10)))]
  except Exception as err:
   ret['log'] = ['ERROR: %s'%(repr(err))]
 return ret

#
#
def sync(aCTX, aArgs = None):
 """ Function doesn't do anything

 Args:
  - id (required). Server id on master node

 Output:
 """
 return None

#
#
def restart(aCTX, aArgs = None):
 """Function provides restart capabilities of service. This should mean a 

 Args:

 Output:
  - code
  - output
  - result 'OK'/'NOT_OK'
 """
 ret = {'code':None, 'output':None, 'status':'OK'}
 try:
  open(aCTX.settings['logs'][aCTX.settings['logger']['log']],'w').close()
  ret['output'] = 'CLEARED'
  aCTX.log("Emptied log [%s]"%(aCTX.settings['logger']['log']))
 except Exception as err:
  ret['output'] = 'ERROR: %s'%(repr(err))

 return ret 

#
#
def notify(aCTX, aArgs = None):
 """Function provides notification service, basic at the moment for development purposes

 Args:
  - node (required). Notify REST node in system
  - message (required)
  - user (optional)
  - channel (optional)

 Output:
  - result ('OK'/'NOT_OK')
  - info (possible notify output)
 """
 from time import localtime, strftime
 ret = {}
 try:
  with open(aCTX.settings['logs'][aCTX.settings['logger']['log']], 'a') as f:
   f.write(str("%s: %s\n"%(strftime('%Y-%m-%d %H:%M:%S', localtime()), aArgs['message'])))
 except Exception as err:
  ret['result'] = 'NOT_OK'
  ret['info'] = 'ERROR: %s'%(repr(err)) 
 else:
  ret['result'] = 'OK'
 return ret
