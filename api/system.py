"""System functions locally available"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

############################### System #################################
#
#
def memory_usage(aCTX, aArgs):
 """Function memory usage retrieves currently used memory

 Args:

 Output:
  - memory
 """
 return None

#
#
def memory_objects(aCTX, aArgs):
 """Function memory objects retrieves number of allocated memory objects

 Args:

 Output:
  - objects. list of objects
 """
 from gc import get_objects
 return {'objects':len(get_objects())}

#
#
def state_queue(aCTX, aArgs):
 """ Function process context workers and watch for locked processes

  Args:
   timeout. seconds to determine liveness, defaults to 10
   log. whether or not to log each thread. Boolean defaults to False

  Output:
   data. list of workers that are locked
 """
 ret = {'data':[], 'status':'OK'}
 for w in aCTX.workers_active():
  if w[2] >= aArgs.get('timeout',10):
   ret['data'].append(w)
   if aArgs.get('log'):
    aCTX.log(f'Worker {w[0]} stuck for {w[2]} seconds with {w[1]}')
 return ret

#
#
def state_ipc(aCTX, aArgs):
 """ Function returns IPC content

  Args:

  Output:
 """
 return {'status':'OK', 'data':aCTX.ipc}

#
#
def sleep(aCTX, aArgs):
 """ Function sleeps for X seconds

 Args:
  - seconds

 Output:
  status
 """
 from time import sleep as time_sleep
 time_sleep(int(aArgs.get('seconds',10)))
 return {'status':'OK'}

#
#
def environment(aCTX, aArgs):
 """Function environment produces non-config environment for nodes

 TODO: move this into a secured access framework (internal only)

 Args:
  - node (optinal)
  - build (optional)

 Output:
 """
 if all(i in aArgs for i in ['node','build']):
  aCTX.log("Node '%(node)s' connected, running version: %(build)s"%aArgs)
 ret = aCTX.environment(aArgs.get('node',aCTX.node))
 for v in ret.get('tokens',{}).values():
  v['expires'] = v['expires'].strftime("%a, %d %b %Y %H:%M:%S GMT")
 return ret

#
#
def report(aCTX, aArgs):
 """ Function generates a system report

 Args:

 Output:
  <data>
 """
 return aCTX.report()

#
#
def reload(aCTX, aArgs):
 """ Function reloads all system modules

 Args:

 Output:
 """
 return {'node':aCTX.node, 'modules':aCTX.module_reload(),'status':'OK'}

################################# AUTH #############################
#
#
def active_users(aCTX, aArgs):
 """ Function retrives active user ( wrt to tokens) with ip addresses. Pull method for syncing active users to auth server

 Args:

 Output:
  - data
 """
 with aCTX.db as db:
  db.query("SELECT id,alias FROM users WHERE id IN (%s)"%','.join([str(v['id']) for v in aCTX.tokens.values()]))
  alias = {x['id']:x['alias'] for x in db.get_rows()}
 return {'data':[{'ip':v['ip'],'alias':alias[v['id']]} for v in aCTX.tokens.values()]}

#
#
def active_sync(aCTX, aArgs):
 """ Function sync authentication servers vs the token database. Pushes active users to services

 Args:

 Output:
 """
 return {'function':'system_active_sync','users':aCTX.auth_sync()}

################################# REST #############################
#
#
def rest_explore(aCTX, aArgs):
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
  except Exception as e:
   data['error'] = repr(e)
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
def rest_information(aCTX, aArgs):
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

####################################### Logs #######################################
#
#
def logs_clear(aCTX, aArgs):
 """Function docstring for logs_clear TBD

 Args:
  - name (optional)

 Output:
 """
 ret = {'node':aCTX.node,'file':{},'status':'OK'}
 for name,v in aCTX.config['logging'].items():
  if isinstance(v,dict) and v.get('enabled') is True and aArgs.get('name',name) == name:
   try:
    open(v['file'],'w').close()
    ret['file'][name] = 'CLEARED'
    aCTX.log("Emptied log [%s]"%name)
   except Exception as err:
    ret['file'][name] = 'ERROR: %s'%(repr(err))
    ret['status'] = 'NOT_OK'
 return ret

#
#
def logs_get(aCTX, aArgs):
 """Function docstring for logs_get TBD

 Args:
  - count (optional)
  - name (optional)

 Output:
 """
 ret = {}
 count = int(aArgs.get('count',15))
 for name,v in aCTX.config['logging'].items():
  if isinstance(v,dict) and v.get('enabled') is True and aArgs.get('name',name) == name:
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
def file_list(aCTX, aArgs):
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
  if 'directory' in aArgs:
   ret['path'] = 'files/%s'%aArgs['directory']
   directory = aCTX.config['files'][aArgs['directory']]
  elif 'fullpath' in aArgs:
   directory = aArgs['fullpath']
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
def database_backup(aCTX, aArgs):
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
def node_to_api(aCTX, aArgs):
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
def worker(aCTX, aArgs):
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
  aCTX.schedule_api_task(aArgs['module'],aArgs['function'],int(aArgs.get('frequency',0)), output = aArgs.get('output',False), args = aArgs.get('args',{}))
  return {'status':'OK'}
 else:
  return {'status':'NOT_OK'}

#
#
def task_list(aCTX, aArgs):
 """ Function returns active task list

 Args:

 Output:
  - data. List of tasks
 """
 return {'data':aCTX.config.get('tasks',[])}

############################## Site ###########################
#
#
def inventory(aCTX, aArgs):
 """Function takes a user_id and produce an inventory for the node, for now until user id passed into functions

 Args:
  - user_id (optional)

 Output:
 """
 ret = aCTX.node_function('master','master','inventory')(aArgs = {'node':aCTX.node,'user_id':aArgs.get('user_id',-1)})
 return ret
