"""MYSQL API module. This module provides system support for mysql DB operations"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

#
#
def dump(aCTX, aArgs = None):
 """ Function dumps database schema or values or full database info

 Args:
  - mode (required) 'structure'/'full'
  - username (optional)
  - password (optional)
  - database (optional)

 Output:
 """
 from subprocess import check_output
 if aArgs.get('username') and aArgs.get('password') and aArgs.get('database'):
  db,username,password = aArgs['database'],aArgs['username'],aArgs['password']
 else:
  db,username,password = aCTX.config['db_name'], aCTX.config['db_user'], aCTX.config['db_pass']
 try:
  line_number = 0
  mode = aArgs.get('mode','structure')
  cmd  = ["mysqldump", "-u" + username, "-p" + password, db]
  output = []

  if   mode == 'structure':
   cmd.extend(['--no-data','--add-drop-database'])
  elif mode == 'database':
   output.append("SET sql_mode='NO_AUTO_VALUE_ON_ZERO';")
   cmd.extend(['-c','--skip-extended-insert'])

  if aArgs.get('full',True):
   output.extend(["DROP DATABASE IF EXISTS %s;"%db,"CREATE DATABASE %s;"%db])
  else:
   cmd.extend(['--no-create-info','--skip-triggers'])
  output.append("USE %s;"%db)
  # print(" ".join(cmd))
  data = check_output(cmd).decode()
  for line in data.split('\n'):
   line_number+=1
   if not line[:2] in [ '/*','--']:
    if "AUTO_INCREMENT=" in line:
     parts = line.split();
     for indx, part in enumerate(parts):
      if "AUTO_INCREMENT=" in part:
       parts.remove(part)
       break
     line = " ".join(parts)
    # print("%05d: %s"%(line_number,line))
    output.append(line)
  res = 'OK'
 except Exception as e:
  output = ["DumpError(%s)@%s"%(repr(e),line_number)]
  res = 'NOT_OK'
 return {'status':res, 'output':output,'mode':mode,'full':aArgs.get('full',True)}

#
#
def restore(aCTX, aArgs = None):
 """ Function restores database schema or values or full database info, Caution (!) if restoring a schema there will be no/0 rows in any table in the database

 Args:
  - username (optional)
  - password (optional)

 Output:
  - result
 """
 from subprocess import check_output
 if aArgs.get('username') and aArgs.get('password'):
  username,password = aArgs['username'],aArgs['password']
 else:
  username,password = aCTX.config['db_user'], aCTX.config['db_pass']

 try:
  cmd  = ["mysql","--init-command='SET SESSION FOREIGN_KEY_CHECKS=0;'", "-u%s"%username, "-p%s"%password, '<',aArgs['file']]
  output = check_output(" ".join(cmd), shell=True).decode()
  return { 'status':'OK','output':output.split('\n') }
 except Exception as e:
  return {'status':'NOT_OK', 'output':[repr(e)] }

#
#
def diff(aCTX, aArgs = None):
 """ Function makes a diff between current database schema and the supplied schema file.

 Args:
  - schema_file (required)
  - username (optional)
  - password (optional)
  - database (optional)

 Output:
  - diffs. counter
  - output. list of lines indicating where the diff is
 """

 from difflib import unified_diff
 with open(aArgs['schema_file']) as f:
  data = f.read()
 ret = {}
 aArgs.update({'mode':'structure'})
 db = dump(aCTX, aArgs)
 ret['source'] = db['status']
 ret['output'] = [line for line in unified_diff(db['output'],data.split('\n'),fromfile='dbase',tofile=aArgs['schema_file'])]
 ret['diffs'] = 0
 for line in ret['output']:
  if "@@" in line:
   ret['diffs'] += 1
 return ret

#
#
def patch(aCTX, aArgs = None):
 """ Function patches current database schema with the supplied schema file. If not successful it will try to restore entire old database. Intermediate files are mysql.backup (entire DB) and mysql.values (INSERTs only - used for restoring) 

 Args:
  - schema_file (required)
  - username (optional)
  - password (optional)
  - database (optional)

 Output:
 """
 from os import remove
 ret = {'status':'NOT_OK'}
 args = dict(aArgs)
 args.update({'mode':'database','full':True})

 res = dump(aCTX, args)
 ret['database_backup_result'] = res['status']
 with open('mysql.backup','w', encoding='utf-8') as f:
  f.write(u'\n'.join(res['output']))

 args['full'] = False
 res = dump(aCTX, args)
 ret['data_backup_result'] = res['status']
 with open('mysql.values','w', encoding='utf-8') as f:
  f.write(u'\n'.join(res['output']))

 if ret['database_backup_result'] == 'OK' and ret['data_backup_result'] == 'OK':
  args['file'] = aArgs['schema_file']
  res = restore(aCTX, args)
  ret['struct_install_result']= res['status']
  if not res['status'] == 'OK':
   ret['struct_install_error']= res['output']
  else:
   args['file'] = 'mysql.values'
   res = restore(aCTX, args)
   ret['data_restore_result'] = res['status']
   if not res['status'] == 'OK':
    ret['data_restore_error'] = res['output']
    ret['data_restore_extra'] = "Warning - patch failed, trying to restore old data"
    args['file'] = 'mysql.backup'
    res = restore(aCTX, args)
    ret['database_restore_result'] = res['status']
    ret['database_restore_output'] = res['output']
   else:
    remove('mysql.backup')
    remove('mysql.values')
    ret['status'] = 'OK'
 return ret
