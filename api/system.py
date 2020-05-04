"""System functions locally available"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

############################### System #################################
#
#
def memory_usage(aCTX, aArgs = None):
 """Function memory usage retrieves currently used memory

 Args:

 Output:
  - memory
 """
 return None

#
#
def memory_objects(aCTX, aArgs = None):
 """Function memory objects retrieves number of allocated memory objects

 Args:

 Output:
  - objects. list of objects
 """
 from gc import get_objects
 return {'objects':len(get_objects())}

#
#
def garbage_collect(aCTX, aArgs = None):
 """Function garbage_collect performs a garbage collection

 Args:

 Output:
 """
 from gc import collect
 return {'collected':collect()}

#
#
def sleep(aCTX, aArgs = None):
 """ Function sleeps for X seconds

 Args:
  - seconds

 Output:
  status
 """
 from time import sleep
 sleep(int(aArgs.get('seconds',10)))
 return {'status':'OK'}

#
#
def error(aCTX, aArgs = None):
 """ Function throws an error """
 return (test == 'error')

#
#
def external_ip(aCTX, aArgs = None):
 """Function docstring for external_ip. TBD

 Args:

 Output:
 """
 ret ={}
 from rims.core.genlib import external_ip
 try:  ret['ip'] = external_ip()
 except Exception as e:
  ret['status'] = 'NOT_OK'
  ret['info'] = str(e)
 else:
  ret['status'] = 'OK'
 return ret

#
#
def environment(aCTX, aArgs = None):
 """Function environment produces non-config environment for nodes

 Args:
  - node (optinal)
  - build (optional)

 Output:
 """
 if all(i in aArgs for i in ['node','build']):
  aCTX.log("Node '%(node)s' connected, running version: %(build)s"%aArgs)
 ret = aCTX.system_environment(aArgs.get('node',aCTX.node))
 for k,v in ret['tokens'].items():
  v['expires'] = v['expires'].strftime("%a, %d %b %Y %H:%M:%S GMT")
 return ret

#
#
def mode(aCTX, aArgs = None):
 """ Function sets run mode

 Args:
  - mode (optional) - 'api'/'debug'

 Output:
 """
 if 'mode' in aArgs and aArgs['mode'] in ['api','debug']:
  aCTX.config['mode'] = aArgs['mode']
 return {'mode':aCTX.config['mode']}

#
#
def report(aCTX, aArgs = None):
 """ Function generates a system report

 Args:

 Output:
  <data>
 """
 return aCTX.report()

#
#
def reload(aCTX, aArgs = None):
 """ Function reloads all system modules

 Args:
  node (optional)

 Output:
 """
 if aArgs.get('node',aCTX.node) != aCTX.node:
  try:
   ret = aCTX.node_function(aArgs['node'],'system','reload')(aArgs = aArgs)
  except Exception as e:
   ret = {'node':aArgs['node'],'modules':[],'status':'NOT_OK','info':'Remote reload error: %s'%str(e)}
 else:
  ret = {'node':aCTX.node, 'modules':aCTX.module_reload(),'status':'OK'}
 return ret

#
#
def shutdown(aCTX, aArgs = None):
 """ Function shuts down system (!!!)

 Args:

 Output:
 """
 from threading import Thread
 from time import sleep
 def __shutdown():
  sleep(1)
  aCTX.close()
 process = Thread(target=__shutdown, args=[])
 process.start()
 return {'status':'OK','state':'shutdown in progress'}

################################# REST #############################
#
#
def rest_explore(aCTX, aArgs = None):
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
   module = import_module("rims.api.%s"%(aFile))
   data['functions'] = [item for item in dir(module) if item[0:2] != "__" and isinstance(getattr(module,item,None),function)]
  except Exception as e: data['error'] = repr(e)
  return data

 ret = {'data':[]}
 if 'api' in aArgs:
  ret['data'].append(__analyze(aArgs['api']))
 else:
  from os import path as ospath, listdir
  restdir = ospath.abspath(ospath.join(ospath.dirname(__file__)))
  for restfile in listdir(restdir):
   if restfile[-3:] == '.py':
    ret['data'].append(__analyze(restfile[0:-3]))
 return ret

#
#
def rest_information(aCTX, aArgs = None):
 """ rest_information provides easy access to docstring for api/function

 Args:
  - api (required)
  - function (required)

 Output:
 """
 from importlib import import_module
 try:
  mod = import_module("rims.api.%s"%(aArgs['api']))
  fun = getattr(mod,aArgs['function'],None)
  return {'api':aArgs['api'],'module':mod.__doc__.split('\n'),'information':fun.__doc__.split('\n')}
 except:
  return {'status':'NOT_OK','info':'api and function arguments required'}

############################### Services ################################
#
#
def service_list(aCTX, aArgs = None):
 """Function service_list returns externally configured, non-RIMS services

 Args:

 Output:
 """
 return {'services':[{'name':x,'service':aCTX.config['services'][x]} for x in list(aCTX.config.get('services',{}).keys())]}

#
#
def service_info(aCTX, aArgs = None):
 """Function docstring for service_info. TBD

 Args:
  - service  (required)
  - op (optional): 'start','stop'

 Output:
  - status
  - state
  - code (operation return code)
 """
 from subprocess import check_output, CalledProcessError
 ret = {'state':None,'status':'OK'}
 if 'op' in aArgs:
  from time import sleep
  try:
   command = "sudo /etc/init.d/%(service)s %(op)s"%aArgs
   ret['result'] = check_output(command.split()).decode().strip()
  except CalledProcessError as c:
   ret['info'] = c.output.strip()
   ret['status'] = 'NOT_OK'
  else:
   sleep(2)

 try:
  command = "sudo /etc/init.d/%(service)s status"%aArgs
  output = check_output(command.split())
  ret['code'] = 0
 except CalledProcessError as c:
  output = c.output
  ret['code'] = c.returncode

 for line in output.decode().split('\n'):
  line = line.lstrip()
  if (line.lstrip())[0:7] == 'Active:':
   state = line[7:].split()
   ret['state'] = state[0]
   ret['extra'] = state[1][1:-1]
   break
 return ret

####################################### Logs #######################################
#
#
def logs_clear(aCTX, aArgs = None):
 """Function docstring for logs_clear TBD

 Args:
  - name (optional)

 Output:
 """
 ret = {'node':aCTX.node,'file':{}}
 for name,v in aCTX.config['logging'].items():
  if type(v) == dict and v.get('enabled') == True and aArgs.get('name',name) == name:
   try:
    open(v['file'],'w').close()
    ret['file'][name] = 'CLEARED'
    aCTX.log("Emptied log [%s]"%name)
   except Exception as err:
    ret['file'][name] = 'ERROR: %s'%(repr(err))
 return ret

#
#
def logs_get(aCTX, aArgs = None):
 """Function docstring for logs_get TBD

 Args:
  - count (optional)
  - name (optional)

 Output:
 """
 ret = {}
 count = int(aArgs.get('count',15))
 for name,v in aCTX.config['logging'].items():
  if type(v) == dict and v.get('enabled') == True and aArgs.get('name',name) == name:
   lines = ["\r" for i in range(count)]
   pos = 0
   try:
    with open(v['file'],'r') as f:
     for line in f:
      lines[pos] = line
      pos = (pos + 1) % count
     ret[name] = [lines[(pos + n) % count][:-1] for n in reversed(list(range(count)))]
   except Exception as err:
    ret[name] = ['ERROR: %s'%(repr(err))]
 return ret

################################# File ############################
#
#
def file_list(aCTX, aArgs = None):
 """Function list files in directory pinpointed by directory (in config at the node) or by fullpath

 Args:
  - directory (optional required)
  - fullpath (optional required)

 Output:
  - List of files in 'files'
  - 'path' relative the api to access the files

 """
 from os import path as ospath, listdir
 ret = {'files':[]}
 try:
  if 'fullpath' in aArgs:
   directory = aArgs['fullpath']
  elif 'directory' in aArgs:
   ret['path'] = 'files/%s'%aArgs['directory']
   directory = aCTX.config['files'][aArgs['directory']]
  else:
   ret['path'] = 'images'
   directory = 'public/images'
  for file in listdir(ospath.abspath(directory)):
   ret['files'].append(file)
 except Exception as e:
  ret['info'] = repr(e)
  ret['status'] = 'NOT_OK'
 else:
  ret['status'] = 'OK'
 ret['files'].sort()
 return ret

############################## Database ######################
#
#
def database_backup(aCTX, aArgs = None):
 """Function docstring for database_backup. Does Database Backup to file

 Args:
  - filename (required)

 Output:
 """
 from rims.api.mysql import dump
 ret  = {'filename':aArgs['filename']}
 data = dump(aCTX, {'mode':'database'})['output']
 try:
  with open(ret['filename'],'w+') as f:
   output = "\n".join(data)
   f.write(output)
  ret['status'] = 'OK'
 except Exception as err:
  ret['error'] = repr(err)
  ret['status'] = 'NOT_OK'
 return ret

#
#
def node_to_api(aCTX, aArgs = None):
 """ Function returns api for a specific node name

 Args:
  - node

 Output:
  - url
 """
 return {'url':aCTX.nodes[aArgs['node']]['url']}

############################## Tasks ###########################
#
#
def worker(aCTX, aArgs = None):
 """Function instantiate a worker thread with arguments

 Args:
  - module (required)
  - function (required)
  - args (optional)
  - frequency (optional required, 0 for transients)
  - output (optional)

 Output:
  - result
 """
 if all(i in aArgs for i in ['module','function']):
  aCTX.workers.schedule_task(aArgs['module'],aArgs['function'],int(aArgs.get('frequency',0)), output = aArgs.get('output',False), args = aArgs.get('args',{}))
  return {'status':'OK'}
 else:
  return {'status':'NOT_OK'}