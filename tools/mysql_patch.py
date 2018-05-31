#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"
__version__ = "18.05.31GA"
__status__ = "Production"

#
#
if __name__ == "__main__":
 from sys import path as syspath, argv, exit,stdout
 if len(argv) < 2:
  print argv[0] + " [struct-file]"
  exit(0)

 from os import path as ospath, getcwd, remove
 syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..')))
 from sdcp.rest import mysql

 file = ospath.abspath(ospath.join(getcwd(),argv[1]))
 ret = {}
 with open('mysql.backup','w') as f:
  res = mysql.dump({'mode':'database','full':True})
  ret['backup_all'] = res['res']
  f.write("\n".join(res['output']))

 with open('mysql.values','w') as f:
  res = mysql.dump({'mode':'database','full':False})
  ret['save_data'] = res['res']
  f.write("\n".join(res['output']))

 if ret['backup_all'] == 'OK' and ret['save_data'] == 'OK':
  res = mysql.restore({'file':file})
  ret['install_struct']= res['res']
  if not res['res'] == 'OK':
   ret['error']= res['output']
  else:
   res = mysql.restore({'file':'mysql.values'})
   ret['restore_data'] = res['res']
   if not res['res'] == 'OK':
    ret['error'] = res['output']
    stdout.write("\n!! Warning - patch failed, trying to restore old data !!\n\n")
    res = mysql.restore({'file':'mysql.backup'})
    ret['restore_backup'] = res['res']
    ret['restore_result'] = res['output']
   else:
    remove('mysql.backup')
    remove('mysql.values')
 stdout.write("%s\n"%(ret))
