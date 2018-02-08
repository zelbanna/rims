__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"


#
# dump(mode,full)
def dump(aDict):
 from subprocess import check_output
 from .. import SettingsContainer as SC
 try:
  db = SC.database['database']
  mode = aDict.get('mode','structure')
  cmd  = ["mysqldump", "-u" + SC.database['username'], "-p" + SC.database['password'], db]

  if   mode == 'structure':
   cmd.extend(['--no-data','--add-drop-database'])
  elif mode == 'database':
   cmd.extend(['-c','--skip-extended-insert'])

  output = []
  if aDict.get('full',True):
   output.extend(["DROP DATABASE IF EXISTS "+db+";","CREATE DATABASE "+db+";"])
  else:
   cmd.extend(['--no-create-info','--skip-triggers'])
  output.append("USE " + db + ";")
  data = check_output(cmd)
  for line in data.split('\n'):
   if not line[:2] in [ '/*','--']:
    if "AUTO_INCREMENT=" in line:
     parts = line.split();
     for index, part in enumerate(parts):
      if "AUTO_INCREMENT=" in part:
       parts.remove(part)
       break
     line = " ".join(parts)
    output.append(line)
  res = 'OK'
 except Exception,e:
  output = ["DumpError:{}".format(str(e))]
  res = 'NOT_OK'
 return {'res':res, 'output':output}

#
#
def restore(aDict):
 from subprocess import check_output
 if aDict.get('username') and aDict.get('password'):
  username,password = aDict['username'],aDict['password']
 else:
  from .. import SettingsContainer as SC
  username,password = SC.database['username'], SC.database['password']

 try:
  cmd  = ["mysql","--init-command='SET SESSION FOREIGN_KEY_CHECKS=0;'", "-u%s"%username, "-p%s"%password, '<',aDict['file']]
  output = check_output(" ".join(cmd), shell=True)
  return { 'res':'OK','output':output.split('\n') }
 except Exception,e:
  return {'res':'NOT_OK', 'output':[str(e)] }

#
#
def diff(aDict):
 from difflib import unified_diff
 with open(aDict['file']) as f:
  data = f.read() 
 ret = {}
 db = dump({'mode':'structure'})
 ret['database'] = db['res']
 ret['output'] = [line for line in unified_diff(db['output'],data.split('\n'),fromfile='dbase',tofile=aDict['file'])]
 ret['diffs'] = 0
 for line in ret['output']:
  if "@@" in line:
   ret['diffs'] += 1
 return ret
