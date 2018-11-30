#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"

#
#
if __name__ == "__main__":
 from sys import path as syspath, argv, exit, stdout
 if len(argv) < 3:
  print(argv[0] + " <config.json> <db-struct-file-to-compare>")
  exit(0)

 from os import path as ospath, getcwd
 syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..')))
 from rims.rest import mysql
 from rims.core.engine import Context
 from json import load

 diffs= mysql.diff(Context(aConfig = argv[1]), {"schema_file":ospath.abspath(ospath.join(getcwd(),argv[2]))})
 print("Number of diffs: %s\n___________________________________"%diffs['diffs'])
 for line in diffs['output']:
  print(line.rstrip('\n'))
