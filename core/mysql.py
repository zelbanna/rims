__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

from subprocess import check_output
from sdcp import PackageContainer as PC

#
# dump(file | pointer)
def dump(aDict):
 try:
  mode = aDict.get('mode','structure')
  cmd  = ["mysqldump", "-u" + PC.generic['dbuser'], "-p" + PC.generic['dbpass'], PC.generic['db']]

  if   mode == 'structure':
   cmd.extend(['--no-data','--add-drop-database'])
  elif mode == 'database':
   cmd.extend(['-c','--skip-extended-insert'])

  output = ""
  if aDict.get('full',True):
   output += "DROP DATABASE IF EXISTS {0};\nCREATE DATABASE {0};\nUSE {0};\n".format(PC.generic['db'])
  else:
   cmd.extend(['--no-create-info','--skip-triggers'])

  output += ("--\n-- Command:" + " ".join(cmd) + "n--\n")
  data = check_output(cmd)
  for line in data.split('\n'):
   if not line[:2] in [ '/*','--']:
    if "AUTO_INCREMENT=" in line:
     parts = line.split();
     for index, part in enumerate(parts):
      if "AUTO_INCREMENT=" in part:
       parts[index] = ''
     line = " ".join(parts)
    output += (line + '\n')
  res = 'OK'
 except Exception,e:
  print "DumpError:{}".format(str(e))
  res = 'NOT_OK'
 return {'res':res, 'output':output}

#
#
def restore(aDict):
 try:
  cmd  = ["mysql","--init-command='SET SESSION FOREIGN_KEY_CHECKS=0;'", "-u{}".format(PC.generic['dbuser']), "-p{}".format(PC.generic['dbpass']), '<',aDict['file']]
  output = check_output("{}".format(" ".join(cmd)), shell=True)
  return { 'res':'OK','output':output }
 except Exception,e:
  print "DumpError:{}".format(str(e))
  return {'res':'NOT_OK', 'output':str(e) }

#
#
def diff(aDict):
 from tempfile import NamedTemporaryFile
 with NamedTemporaryFile() as f:
  res = dump({'pointer':f,'mode':'structure'})
