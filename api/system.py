"""System functions locally available"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

from os import path as ospath, listdir
from importlib import import_module

############################### System #################################
#
#
def traceback(aRT, aArgs):
 from traceback import format_stack
 from sys import _current_frames as current_frames
 return {tid:format_stack(stack) for tid,stack in current_frames().items()}

#
#
def memory_usage(aRT, aArgs):
 """Function memory usage retrieves currently used memory

 Args:

 Output:
  - memory
 """
 return None

#
#
def memory_objects(aRT, aArgs):
 """Function memory objects retrieves number of allocated memory objects

 Args:

 Output:
  - objects. list of objects
 """
 from gc import get_objects
 return {'objects':len(get_objects())}

#
#
def state_queue(aRT, aArgs):
 """ Function process context workers and watch for locked processes

  Args:
   - timeout. seconds to determine liveness, defaults to 10
   - log. whether or not to log each thread. Boolean defaults to False

  Output:
   data. list of workers that are locked
 """
 ret = {'data':[], 'status':'OK'}
 for w in aRT.workers_active():
  if w[2] >= aArgs.get('timeout',10):
   ret['data'].append(w)
   if aArgs.get('log'):
    aRT.log(f'Worker {w[0]} stuck for {w[2]} seconds with {w[1]}')
 return ret

#
#
def environment(aRT, aArgs):
 """Function environment produces non-config environment for nodes

 TODO: move this into a secured access framework (internal only)

 Args:
  - node (optinal)
  - build (optional)

 Output:
 """
 if all(i in aArgs for i in ['node','build']):
  aRT.log("Node '%(node)s' connected, running version: %(build)s"%aArgs)
 ret = aRT.environment(aArgs.get('node',aRT.node))
 for v in ret.get('tokens',{}).values():
  v['expires'] = v['expires'].strftime("%a, %d %b %Y %H:%M:%S GMT")
 return ret

#
#
def report(aRT, aArgs):
 """ Function generates a system report

 Args:

 Output:
  <data>
 """
 return aRT.report()

#
#
def reload(aRT, aArgs):
 """ Function reloads all system modules

 Args:

 Output:
 """
 return {'node':aRT.node, 'modules':aRT.module_reload(),'status':'OK'}

################################# AUTH #############################
#
#
def active_users(aRT, aArgs):
 """ Function retrives active user ( wrt to tokens) with ip addresses. Pull method for syncing active users to auth server

 Args:

 Output:
  - data
 """
 with aRT.db as db:
  db.query("SELECT id,alias FROM users WHERE id IN (%s)"%','.join([str(v['id']) for v in aRT.tokens.values()]))
  alias = {x['id']:x['alias'] for x in db.get_rows()}
 return {'data':[{'ip':v['ip'],'alias':alias[v['id']]} for v in aRT.tokens.values()]}

#
#
def active_sync(aRT, aArgs):
 """ Function sync authentication servers vs the token database. Pushes active users to services

 Args:

 Output:
 """
 return {'function':'system_active_sync','users':aRT.auth_sync()}

################################# REST #############################
#
#
def rest_explore(aRT, aArgs):
 """Function docstring for rest_explore TBD

 Args:
  - api (optional)

 Output:
 """
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
  restdir = ospath.abspath(ospath.join(ospath.dirname(__file__)))
  for restfile in listdir(restdir):
   if restfile[-3:] == '.py':
    ret['data'].append(__analyze(restfile[0:-3]))
 return ret

#
#
def rest_information(aRT, aArgs):
 """ rest_information provides easy access to docstring for api/function

 Args:
  - api (required)
  - function (required)

 Output:
 """
 try:
  mod = import_module("rims.api.%s"%(aArgs['api']))
  fun = getattr(mod,aArgs['function'],None)
  return {'api':aArgs['api'],'module':mod.__doc__.split('\n'),'information':fun.__doc__.split('\n')}
 except:
  return {'status':'NOT_OK','info':'api and function arguments required'}

####################################### Logs #######################################
#
#
def logs_clear(aRT, aArgs):
 """Function docstring for logs_clear TBD

 Args:
  - name (optional)

 Output:
 """
 ret = {'node':aRT.node,'file':{},'status':'OK'}
 for name,v in aRT.config['logging'].items():
  if isinstance(v,dict) and v.get('enabled') is True and aArgs.get('name',name) == name:
   try:
    open(v['file'],'w').close()
    ret['file'][name] = 'CLEARED'
    aRT.log("Emptied log [%s]"%name)
   except Exception as err:
    ret['file'][name] = 'LOGS_ERROR: %s'%(repr(err))
    ret['status'] = 'NOT_OK'
 return ret

#
#
def logs_get(aRT, aArgs):
 """Function docstring for logs_get TBD

 Args:
  - count (optional)
  - name (optional)

 Output:
 """
 ret = {}
 count = int(aArgs.get('count',15))
 for name,v in aRT.config['logging'].items():
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
    ret[name] = ['LOGS_ERROR: %s'%(repr(err))]
 return ret

################################# File ############################
#
#
def file_list(aRT, aArgs):
 """Function list files in directory pinpointed by directory (in config at the node) or by fullpath

 Args:
  - directory (optional required)
  - fullpath (optional required)

 Output:
  - List of files in 'files'
  - 'path' relative the api to access the files

 """
 ret = {'files':[]}
 try:
  if 'directory' in aArgs:
   ret['path'] = 'files/%s'%aArgs['directory']
   directory = aRT.config['files'][aArgs['directory']]
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
def database_backup(aRT, aArgs):
 """Function docstring for database_backup. Does Database Backup to file

 Args:
  - filename (required)

 Output:
 """
 from rims.api.mysql import dump
 ret  = {'filename':aArgs['filename']}
 data = dump(aRT, {'mode':'database'})['output']
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
def node_to_api(aRT, aArgs):
 """ Function returns api for a specific node name

 Args:
  - node

 Output:
  - url
 """
 return {'url':aRT.nodes[aArgs['node']]['url']}

############################## Tasks ###########################
#
#
def worker(aRT, aArgs):
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
  aRT.schedule_api_task(aArgs['module'],aArgs['function'],int(aArgs.get('frequency',0)), output = aArgs.get('output',False), args = aArgs.get('args',{}))
  return {'status':'OK'}
 else:
  return {'status':'NOT_OK'}

#
#
def task_list(aRT, aArgs):
 """ Function returns active task list

 Args:

 Output:
  - data. List of tasks
 """
 return {'data':aRT.config.get('tasks',[])}

############################## Site ###########################
#
#
def inventory(aRT, aArgs):
 """Function takes a user_id and produce an inventory for the node, for now until user id passed into functions

 Args:
  - user_id (optional)

 Output:
 """
 ret = aRT.node_function('master','master','inventory')(aArgs = {'node':aRT.node,'user_id':aArgs.get('user_id',-1)})
 return ret
