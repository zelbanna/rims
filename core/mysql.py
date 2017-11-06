__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

from subprocess import check_output
from sdcp import PackageContainer as PC

def dump(aDict):
 try:
  mode = aDict.get('mode','structure')
  cmd  = ["mysqldump", "-u{}".format(PC.generic['dbuser']), "-p{}".format(PC.generic['dbpass']), PC.generic['db']]
  if   mode == 'structure':
   cmd.extend(['--no-data','--add-drop-database'])
  elif mode == 'database':
   cmd.extend(['-c','--skip-extended-insert'])
   if not aDict.get('full',True):
    cmd.extend(['--no-create-info','--skip-triggers'])
  data = check_output(cmd)
  print "--\n-- Command: {}\n--".format(" ".join(cmd))
  print "USE {};".format(PC.generic['db'])
  for line in data.split('\n'):
   if not line[:2] in [ '/*','--']:
    if "AUTO_INCREMENT=" in line:
     parts = line.split();
     for index, part in enumerate(parts):
      if "AUTO_INCREMENT=" in part:
       parts[index] = ''
     line = " ".join(parts)
    print line
  res = 'OK'
 except Exception,e:
  print "DumpError:{}".format(str(e))
  res = 'NOT_OK'
 return {'res':res}

def restore(aDict):
 try:
  cmd  = ["mysql","--init-command='SET SESSION FOREIGN_KEY_CHECKS=0;'", "-u{}".format(PC.generic['dbuser']), "-p{}".format(PC.generic['dbpass']), '<',aDict['file']]
  output = check_output("{}".format(" ".join(cmd)), shell=True)
  return { 'res':'OK','info':output }
 except Exception,e:
  print "DumpError:{}".format(str(e))
  return {'res':'NOT_OK', 'info':str(e) }
