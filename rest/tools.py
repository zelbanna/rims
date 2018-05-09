"""SDCP tools REST module. Provides various tools that are not bound to a node"""
__author__ = "Zacharias El Banna"
__version__ = "18.04.07GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)
__node__ = 'any'

#
#
def debug(aDict):
 """Function docstring for debug TBD

 Args:

 Output:
 """ 
 print "Set-Cookie: debug=true; Path=/"
 from sys import path as syspath 
 return { 'globals':[x for x in globals().keys() if not x[0:2] == '__'], 'path':syspath }

############################################ REST tools ############################################
#
#
def rest_analyze(aDict):
 """Function docstring for rest_analyze. Analyzes REST files to deduce parameter inputs

 Args:
  - file (required)

 Output:
 """
 restdir = ospath.abspath(ospath.join(ospath.dirname(__file__), '..','rest'))
 ret = {'file':aDict['file'],'functions':[],'global':[]}
 data = {'function':None,'required':{},'optional':{},'pop':{},'undecoded':[],'arg':None,'imports':[]}

 with open(ospath.abspath(ospath.join(restdir,aDict['file'])),'r') as file:
  line_no = 0
  for line in file:
   line_no += 1
   line = line.rstrip()
   line = line.replace("%s","<var>")
   if line[0:4] =='from':
    ret['global'].append(line)
   if line[0:4] == 'def ':
    if data['function']:
     ret['functions'].append(data)
     data = {'function':None,'required':{},'optional':{},'pop':{},'undecoded':[],'arg':None,'imports':[]}
    name_end = line.index('(')
    data['arg'] = line[name_end+1:-2]
    data['function'] = line[4:name_end].lstrip()
   elif data['function'] and data['arg'] in line:
    try:
     parts = line.split(data['arg'])
     for part in parts[1:]:
      if part[0:2] == "['":
       end = part.index("]")
       argument = part[2:end-1]
       if not data['required'].get(argument):
        data['required'][argument] = (data['optional'].get(argument) is None)
      elif part[0:6] == ".get('":
       end = part[6:].index("'")
       argument = part[6:6+end]
       if not data['optional'].get(argument):
        data['optional'][argument] = (data['required'].get(argument) is None)
      elif part[0:6] == ".pop('":
       end = part[6:].index("'")
       argument = part[6:6+end]
       if not data['required'].get(argument) and not data['optional'].get(argument):
        data['pop'][argument] = True
      elif part[0:7]== ".keys()" or part[0] == ")" or part[0:12] == ".iteritems()":
       pass
      else:
       data['undecoded'].append({'part':part,'line':line_no})
    except Exception, e:
     data['undecoded'].append({'error':str(e),'line':line_no})
   elif data['function'] and "from" in line:
    data['imports'].append(line.lstrip())
  if data['function']:
   ret['functions'].append(data)
 return ret


#
#
def rest_explore(aDict):
 """Function docstring for rest_explore TBD

 Args:
  - api (optional)

 Output:
 """
 from types import FunctionType as function
 def __analyze(aFile):
  data = {'api':aFile, 'functions':[]}
  try:
   module = import_module("sdcp.rest.%s"%(aFile))
   data['functions'] = [item for item in dir(module) if item[0:2] != "__" and isinstance(getattr(module,item,None),function)]
  except Exception,e: data['error'] = str(e)
  return data

 ret = {'data':[]}
 if aDict.get('api'):
  ret['data'].append(__analyze(aDict.get('api')))
 else:
  from os import listdir
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
 mod = import_module("sdcp.rest.%s"%(aDict['api']))
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
 from sdcp.SettingsContainer import SC
 from sdcp.core.logger import log
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

 Output:
 """
 from sdcp.SettingsContainer import SC
 ret = {}
 count = int(aDict.get('count',15))
 for name,file in SC['logs'].iteritems():
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

def files_list(aDict):
 """Function docstring for files_list. List files in directory pinpointed by setting (in settings for the node)

 Args:
  - setting (required)                         

 Output: List of files in 'files'
 """
 from os import listdir
 from  sdcp.SettingsContainer import SC
 ret = {'files':[]}
 try:
  ret['directory'] = SC['files'][aDict['setting']] if not aDict['setting'] == 'images' else 'images'
  for file in listdir(ospath.abspath(ret['directory'])):
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
 from sdcp.SettingsContainer import SC
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
   command = "sudo /etc/init.d/%s %s"%(aDict['service'],aDict['op'])
   ret['op'] = check_output(command.split()).strip()
  except CalledProcessError, c:
   ret['op'] = c.output.strip()
  else:
   sleep(2)

 try:
  command = "sudo /etc/init.d/%s status"%aDict['service']
  output = check_output(command.split())
  ret['code'] = 0
 except CalledProcessError, c:
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

#
#
def database_backup(aDict):
 """Function docstring for database_backup. Does Database Backup to file

 Args:
  - filename (required)

 Output:
 """
 ret = {'filename':aDict['filename']}
 from sdcp.SettingsContainer import SC
 if SC['system']['id'] == 'master':
  from mysql import dump
  data = dump({'mode':'database'})['output']
 else:
  data = rest_call("%s?mysql_dump"%settings['system']['master'],{'mode':'database'})['output']
 
 try:
  with open(ret['filename'],'w+') as f:
   f.write("\n".join(data))
  ret['result'] = 'OK'
 except Exception as err:
  ret['error'] = str(err) 
  ret['result'] = 'NOT_OK'
 return ret
