"""

Tools module for various tools


"""
__author__ = "Zacharias El Banna"
__version__ = "4.0GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

#
#
def debug_timeout(aDict):
 """Function tests timeout of client

 Args:
  - sleep (optional)

 Output:
 """
 from time import sleep
 sleep(aDict.get('sleep',10))
 return None

################################## System #################################
#
#
def memory_usage(aDict):
 """Function memory usage retrieves currently used memory

 Args:

 Output:
  - memory
 """
 return None

#
#
def memory_objects(aDict):
 """Function memory objects retrieves number of allocated memory objects

 Args:

 Output:
  - objects. list of objects
 """
 from gc import get_objects
 return {'objects':len(get_objects())}

#
#
def garbage_collect(aDict):
 """Function garbage_collect performs a garbage collection

 Args:

 Output:
 """
 from zdcp.core.common import log
 from gc import collect
 log("Garbage Collection performed")
 return {'collected':collect()}

################################ REST tools ###############################
#
#
def rest_explore(aDict):
 """Function docstring for rest_explore TBD

 Args:
  - api (optional)

 Output:
 """
 from importlib import import_module
 from types import FunctionType as function
 def __analyze(aFile):
  data = {'api':aFile, 'functions':[]}
  try:
   module = import_module("zdcp.rest.%s"%(aFile))
   data['functions'] = [item for item in dir(module) if item[0:2] != "__" and isinstance(getattr(module,item,None),function)]
  except Exception as e: data['error'] = str(e)
  return data

 ret = {'data':[]}
 if aDict.get('api'):
  ret['data'].append(__analyze(aDict.get('api')))
 else:
  from os import listdir, path as ospath
  restdir = ospath.abspath(ospath.join(ospath.dirname(__file__)))
  for restfile in listdir(restdir):
   if restfile[-3:] == '.py':
    ret['data'].append(__analyze(restfile[0:-3]))
 return ret

#
#
def rest_information(aDict):
 """Function docstring for rest_explore TBD

 Args:
  - api (required)
  - function (required)

 Output:
 """
 from importlib import import_module
 mod = import_module("zdcp.rest.%s"%(aDict['api']))
 fun = getattr(mod,aDict['function'],None)
 return {'api':aDict['api'],'module':mod.__doc__.split('\n'),'information':fun.__doc__.split('\n')}

############################################# Logs ###############################################

#
#
def logs_clear(aDict):
 """Function docstring for logs_clear TBD

 Args:

 Output:
 """
 from zdcp.core.common import log
 ret = {'node':SC['system']['id'],'file':{}}
 for name,file in SC['logs'].iteritems():
  try:
   open(file,'w').close()
   ret['file'][name] = 'CLEARED'
   log("Emptied log [{}]".format(name))
  except Exception as err:
   ret['file'][name] = 'ERROR: %s'%(str(err))
 return ret

#
#
def logs_get(aDict):
 """Function docstring for logs_get TBD

 Args:
  - count (optional)
  - name (optional)

 Output:
 """
 ret = {}
 count = int(aDict.get('count',15))
 for name,file in SC['logs'].iteritems():
  if aDict.get('name',name) == name:
   lines = ["\r" for i in range(count)]
   pos = 0
   try:
    with open(file,'r') as f:
     for line in f:
      lines[pos] = line
      pos = (pos + 1) % count
     ret[name] = [lines[(pos + n) % count][:-1] for n in reversed(range(count))]
   except Exception as err:
    ret[name] = ['ERROR: %s'%(str(err))]
 return ret


########################################### FILE ############################################

def file_list(aDict):
 """Function list files in directory pinpointed by directory (in settings for the node) or by fullpath

 Args:
  - directory (optional required)
  - fullpath (optional required)

 Output:
  - List of files in 'files'
  - 'path' relative the api to access the files

 """
 from os import listdir, path as ospath
 ret = {'files':[]}
 try:
  if aDict.get('fullpath'):
   directory = aDict['fullpath']
  elif aDict.get('directory'):
   ret['path'] = '../files/%s'%aDict['directory']
   directory = SC['files'][aDict['directory']]
  else:
   ret['path'] = '../images'
   directory = 'images'
  for file in listdir(ospath.abspath(directory)):
   ret['files'].append(file)
 except Exception as e:
  ret['info'] = str(e)
  ret['result'] = 'NOT_OK'
 else:
  ret['result'] = 'OK'
 ret['files'].sort()
 return ret

######################################### Controls ########################################
#
#
def service_list(aDict):
 """Function docstring for service_list TBD

 Args:

 Output:          
 """
 return {'services':[{'name':x,'service':SC['services'][x]} for x in SC['services'].keys()]}


#
#
def service_info(aDict):
 """Function docstring for service_info. TBD

 Args:
  - service  (required)
  - op (optional): 'start','stop'

 Output:
 """
 from subprocess import check_output, CalledProcessError
 ret = {'state':None}
 if aDict.get('op'):
  from time import sleep
  try:
   command = "sudo /etc/init.d/%(service)s %(op)s"%aDict
   ret['op'] = check_output(command.split()).strip()
  except CalledProcessError as c:
   ret['op'] = c.output.strip()
  else:
   sleep(2)

 try:
  command = "sudo /etc/init.d/%(service)s status"%aDict
  output = check_output(command.split())
  ret['code'] = 0
 except CalledProcessError as c:
  output = c.output
  ret['code'] = c.returncode
 for line in output.split('\n'):
  line = line.lstrip()
  if (line.lstrip())[0:7] == 'Active:':
   state = line[7:].split()
   ret['state'] = state[0]
   ret['info'] = state[1][1:-1]
   break
 return ret

################################### Database ##################################
#
#
def database_backup(aDict):
 """Function docstring for database_backup. Does Database Backup to file

 Args:
  - filename (required)

 Output:
 """
 ret = {'filename':aDict['filename']}
 if SC['system']['id'] == 'master':
  from mysql import dump
  data = dump({'mode':'database'})['output']
 else:
  from zdcp.core.common import rest_call
  res = rest_call("%s/api/mysql_dump"%SC['system']['master'],{'mode':'database'})
  if res['code'] == 200:
   data = res['data']['output']
  else:
   data = []
 try:
  with open(ret['filename'],'w+') as f:
   output = "\n".join(data)
   f.write(output.encode("utf-8"))
  ret['result'] = 'OK'
 except Exception as err:
  ret['error'] = str(err) 
  ret['result'] = 'NOT_OK'
 return ret
