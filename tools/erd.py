#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Dumps the existing database schema into an ERD in path infra/erd.pdf"""
__author__ = "Zacharias El Banna"

from sys import argv, stdout, path as syspath
from json import load,dump,dumps
from os import  path as ospath
basedir = ospath.abspath(ospath.join(ospath.dirname(__file__),'..','..'))
syspath.insert(1, basedir)
res = {}

if len(argv) < 2:
 print("Usage: %s </path/json file>\n"%argv[0])
else:
 with open(ospath.abspath(argv[1]),'r') as sfile:
  config = load(sfile)
 database,host,username,password = config['database']['name'],config['database']['host'],config['database']['username'],config['database']['password']

 try:
  import eralchemy
 except ImportError:
  try:    from pip import main as pipmain
  except: from pip._internal import main as pipmain
  pipmain(["install","-q","eralchemy"])
 else:
  erd_input = "mysql+pymysql://%s:%s@%s/%s"%(username,password,host,database)
  erd_output= ospath.join(basedir,'rims','infra','erd.pdf')
  try:
   from eralchemy import render_er
   render_er(erd_input,erd_output)
   res['status'] = 'OK'
  except Exception as e:
   res['error']  = str(e)
   res['status'] = 'NOT_OK'
  print(dumps(res,indent=4,sort_keys=True))
 exit(0 if res.get('status') == 'OK' else 1)
