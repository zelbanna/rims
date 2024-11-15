"""MYSQL API module. This module provides system support for mysql DB operations"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

from subprocess import check_output
from difflib import unified_diff
from os import remove
from json import dumps

#
#
def dump(aRT, aArgs):
 """ Function dumps database schema or values or full database info

 Args:
  - mode (required) 'schema'/'full'
  - username (optional)
  - password (optional)
  - database (optional)
  - host (optional)

 Output:
 """
 if all(i in aArgs for i in ['username','password','database','host']):
  db,host,username,password = aArgs['database'],aArgs['host'],aArgs['username'],aArgs['password']
 else:
  db,host,username,password = aRT.config['database']['name'], aRT.config['database']['host'], aRT.config['database']['username'], aRT.config['database']['password']

 line_number = 0
 mode = aArgs.get('mode','schema')
 cmd  = ["mysqldump", "--hex-blob", "-u" + username, "-p" + password, '-h',host,db]

 try:
  output = []
  if   mode == 'schema':
   cmd.extend(['--no-data','--add-drop-database'])
  elif mode == 'database':
   output.append("SET sql_mode='NO_AUTO_VALUE_ON_ZERO';")
   cmd.extend(['-c','--skip-extended-insert'])

  if aArgs.get('full',True):
   output.extend(["DROP DATABASE IF EXISTS %s;"%db,"CREATE DATABASE %s;"%db])
  else:
   cmd.extend(['--no-create-info','--skip-triggers'])
  output.append("USE %s;"%db)
  data = check_output(cmd).decode()
  for line in data.split('\n'):
   line_number+=1
   if line[12:17] == "`oui`":
    continue
   elif line[:2] not in [ '/*','--']:
    if "AUTO_INCREMENT=" in line:
     parts = line.split()
     for part in parts:
      if "AUTO_INCREMENT=" in part:
       parts.remove(part)
       break
     line = " ".join(parts)
    output.append(line)
  res = 'OK'
 except Exception as e:
  output = ["DumpError(%s)@%s"%(repr(e),line_number)]
  res = 'NOT_OK'
 return {'status':res, 'output':output,'mode':mode,'full':aArgs.get('full',True),'cmd':' '.join(cmd)}

#
#
def restore(aRT, aArgs):
 """ Function restores database schema or values or full database info, Caution (!) if restoring a schema there will be no/0 rows in any table in the database

 Args:
  - file required
  - username (optional)
  - password (optional)
  - host (optional)

 Output:
  - result
 """
 if all(i in aArgs for i in ['username','password','host']):
  username,password,host = aArgs['username'],aArgs['password'],aArgs['host']
 else:
  username,password,host = aRT.config['database']['username'], aRT.config['database']['password'], aRT.config['database']['host']

 try:
  cmd  = ["mysql","--init-command='SET SESSION FOREIGN_KEY_CHECKS=0;'", "-u%s"%username, "-p%s"%password, '-h',host,'<',aArgs['file']]
  output = check_output(" ".join(cmd), shell=True).decode()
  return { 'status':'OK','output':output.split('\n') }
 except Exception as e:
  return {'status':'NOT_OK', 'output':[repr(e)] }

#
#
def diff(aRT, aArgs):
 """ Function makes a diff between current database schema and the supplied schema file.

 Args:
  - schema_file (required)
  - username (optional)
  - password (optional)
  - database (optional)
  - host (optional)

 Output:
  - diffs. counter
  - output. list of lines indicating where the diff is
 """

 with open(aArgs['schema_file']) as f:
  data = f.read()
 ret = {}
 aArgs.update({'mode':'schema'})
 # INTERNAL from rims.api.mysql import dump
 db = dump(aRT, aArgs)
 ret['source'] = db['status']
 # somehow now there is a now an extra line break... => [:-1]
 ret['output'] = [line for line in unified_diff(db['output'],data.split('\n')[:-1],fromfile='database',tofile=aArgs['schema_file'])]
 ret['diffs'] = 0
 for line in ret['output']:
  if "@@" in line:
   ret['diffs'] += 1
 return ret

#
#
def patch(aRT, aArgs):
 """ Function patches current database schema with the supplied schema file.
 If it is not successful it will try to restore entire old database.
 Intermediate files are: mysql.backup (entire DB) and mysql.values (INSERTs only - used for restoring)

 Args:
  - schema_file (required)
  - username (optional)
  - password (optional)
  - database (optional)
  - host (optional)

 Output:
 """
 ret = {'status':'NOT_OK'}
 args = dict(aArgs)
 args.update({'mode':'database','full':True})

 # INTERNAL from rims.api.mysql import dump
 res = dump(aRT, args)
 ret['database_backup_result'] = res['status']
 with open('mysql.backup','w', encoding='utf-8') as f:
  f.write(u'\n'.join(res['output']))

 args['full'] = False
 # INTERNAL from rims.api.mysql import dump
 res = dump(aRT, args)
 ret['data_backup_result'] = res['status']
 with open('mysql.values','w', encoding='utf-8') as f:
  f.write(u'\n'.join(res['output']))

 if ret['database_backup_result'] == 'OK' and ret['data_backup_result'] == 'OK':
  args['file'] = aArgs['schema_file']
  # INTERNAL from rims.api.mysql import restore
  res = restore(aRT, args)
  ret['struct_install_result']= res['status']
  if res['status'] != 'OK':
   ret['struct_install_error']= res['output']
  else:
   args['file'] = 'mysql.values'
   # INTERNAL from rims.api.mysql import restore
   res = restore(aRT, args)
   ret['data_restore_result'] = res['status']
   if res['status'] != 'OK':
    ret['data_restore_error'] = res['output']
    ret['data_restore_extra'] = "Warning - patch failed, trying to restore old data"
    args['file'] = 'mysql.backup'
    # INTERNAL from rims.api.mysql import restore
    res = restore(aRT, args)
    ret['database_restore_result'] = res['status']
    ret['database_restore_output'] = res['output']
   else:
    remove('mysql.backup')
    remove('mysql.values')
    ret['status'] = 'OK'

 return {'status':ret['status'],'output':dumps(ret,indent=2,sort_keys=True).split('\n')}
