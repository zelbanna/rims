#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"

#
#
from sys import path as syspath, argv, exit, stdout
from os import path as ospath, getcwd
from json import load
from argparse import ArgumentParser
syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..')))
from rims.api import mysql
from rims.core.engine import Context

parser = ArgumentParser(prog='mysql_tools', description = 'MySQL interworking tool')
parser.add_argument('config', help = 'RIMS config file')
parser.add_argument('-d','--diff',    help = 'Compare database schema with schema file', required = False, nargs = 1)
parser.add_argument('-b','--backup',  help = 'Dumps full database',   required = False, action = 'store_true')
parser.add_argument('-s','--schema',  help = 'Dumps database schema', required = False, action = 'store_true')
parser.add_argument('-v','--values',  help = 'Dumps database values', required = False, action = 'store_true')
parser.add_argument('-r','--restore', help = 'Restore with schema and/or values from restore_file', required = False, nargs = 1)
parser.add_argument('-p','--patch',   help = 'Patch database schema with new schema file', required = False, nargs = 1)
input = parser.parse_args()
with open(input.config,'r') as file:
 config = load(file)
ctx = Context(config)

if   input.diff:
 res= mysql.diff(ctx, {"schema_file":ospath.abspath(ospath.join(getcwd(),input.diff[0]))})
 print("Number of diffs: %s\n___________________________________"%res['diffs'])
elif input.backup:
 res = mysql.dump(ctx, {'mode':'database','full':True})
elif input.values:
 res = mysql.dump(ctx, {'mode':'database','full':False})
elif input.schema:
 res = mysql.dump(ctx, {'mode':'schema'})
elif input.restore:
 res = mysql.restore(ctx, {'file':ospath.abspath(ospath.join(getcwd(),input.restore[0]))})
elif input.patch:
 res = mysql.patch(ctx, {'schema_file':ospath.abspath(ospath.join(getcwd(),input.patch[0]))})
else:
 parser.print_help()
 exit(0)

#for line in res['output']:
# print(line)
print("\n".join(res['output']))
