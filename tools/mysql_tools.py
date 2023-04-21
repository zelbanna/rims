#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"

#
#
from argparse import ArgumentParser
from json import load
from sys import path as syspath, exit as sysexit
from os import path as ospath, getcwd
syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..')))
from rims.api import mysql
from rims.core.engine import RunTime
parser = ArgumentParser(prog='mysql_tools', description = 'MySQL interworking tool')
parser.add_argument('-d','--diff',    help = 'Compare database schema with schema file', required = False, nargs = 1)
parser.add_argument('-b','--backup',  help = 'Dumps full database',   required = False, action = 'store_true')
parser.add_argument('-s','--schema',  help = 'Dumps database schema', required = False, action = 'store_true')
parser.add_argument('-v','--values',  help = 'Dumps database values', required = False, action = 'store_true')
parser.add_argument('-r','--restore', help = 'Restore with schema and/or values from restore_file', required = False, nargs = 1)
parser.add_argument('-p','--patch',   help = 'Patch database schema with new schema file', required = False, nargs = 1)
parser.add_argument('-c','--config',  help = 'Config file unless config.json', default='../config.json')
parsedinput = parser.parse_args()
with open(ospath.abspath(ospath.join(ospath.dirname(__file__), parsedinput.config))) as f:
 config = load(f)
ctx = RunTime(config)

if   parsedinput.diff:
 res= mysql.diff(ctx, {"schema_file":ospath.abspath(ospath.join(getcwd(),parsedinput.diff[0]))})
 print(f"Number of diffs: {res['diffs']}\n___________________________________")
elif parsedinput.backup:
 res = mysql.dump(ctx, {'mode':'database','full':True})
elif parsedinput.values:
 res = mysql.dump(ctx, {'mode':'database','full':False})
elif parsedinput.schema:
 res = mysql.dump(ctx, {'mode':'schema'})
elif parsedinput.restore:
 res = mysql.restore(ctx, {'file':ospath.abspath(ospath.join(getcwd(),parsedinput.restore[0]))})
elif parsedinput.patch:
 res = mysql.patch(ctx, {'schema_file':ospath.abspath(ospath.join(getcwd(),parsedinput.patch[0]))})
else:
 parser.print_help()
 sysexit(0)

#for line in res['output']:
# print(line)
print("\n".join(res['output']))
