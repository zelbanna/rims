"""SDCP tools REST module. Provides various tools"""
__author__ = "Zacharias El Banna"
__version__ = "18.03.14GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)


def test(aDict):
 return {'globals':[x for x in globals().keys() if x[0:2] != '__'] }

############################################ REST tools ############################################
#
#
def rest_analyze(aDict):
 """Function docstring for rest_analyze. Analyzes REST files to deduce parameter inputs

 Args:
  - file (required)

 Output:
 """
 from os import path as ospath
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
 from importlib import import_module
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
  from os import path as ospath, listdir
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
 mod = import_module("sdcp.rest.%s"%(aDict['api']))
 fun = getattr(mod,aDict['function'],None)
 return {'api':aDict['api'],'module':mod.__doc__.split('\n'),'information':fun.__doc__.split('\n')}

#
#
def rest_debug(aDict):
 """Function docstring for rest_debug TBD

 Args:

 Output:
 """ 
 print "Set-Cookie: debug=true; Path=/"
 return { 'globals':str(globals().keys()), 'locals':str(locals().keys()) }

############################################ Monitor ##############################################

#
#
def logs_clear(aDict):
 """Function docstring for logs_clear TBD

 Args:

 Output:
 """
 from ..SettingsContainer import SC
 from ..core.logger import log
 ret = {}
 for name,file in SC['logs'].iteritems():
  try:
   open(file,'w').close()
   ret[name] = 'CLEARED'
   log("Emptied log [{}]".format(name))
  except Exception as err:
   ret[name] = 'ERROR: %s'%(str(err))
 return ret

#
#
def logs_get(aDict):
 """Function docstring for logs_get TBD

 Args:
  - count (optional)

 Output:
 """
 from ..SettingsContainer import SC
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
