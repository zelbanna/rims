#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Dumps the existing database schema into an ERD in path infra/erd.pdf"""
__author__ = "Zacharias El Banna"

from sys import exit, stdout, path as syspath
from json import load,dump,dumps
from os import  path as ospath
basedir = ospath.abspath(ospath.join(ospath.dirname(__file__),'..','..'))
syspath.insert(1, basedir)
res = {}
from argparse import ArgumentParser
parser = ArgumentParser(prog='erd', description = 'Generate ERD diagram')
parser.add_argument('-c','--config',  help = 'Config unless config.json', default='../config.json')
input = parser.parse_args()
try:
 with open(ospath.abspath(ospath.join(ospath.dirname(__file__), input.config))) as f:
  config = load(f)['database']
 database,host,username,password = config['name'],config['host'],config['username'],config['password']
except:
 exit(1)
else:
 try:
  import eralchemy
 except ImportError:
  try:    from pip import main as pipmain
  except: from pip._internal import main as pipmain
  pipmain(["install","-q","eralchemy"])
 else:
  erd_input = "mysql+pymysql://%s:%s@%s/%s"%(username,password,host,database)
  erd_output= ospath.join(basedir,'rims','static','erd.pdf')
  try:
   from eralchemy import render_er
   render_er(erd_input,erd_output)
   res['status'] = 'OK'
  except Exception as e:
   res['error']  = str(e)
   res['status'] = 'NOT_OK'
  print(dumps(res,indent=4,sort_keys=True))
 exit(0 if res.get('status') == 'OK' else 1)
