#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Use the database schema for an ERD in path static/erd.pdf"""
__author__ = "Zacharias El Banna"

from argparse import ArgumentParser
from json import load,dumps
from os import  path as ospath
from sys import exit as sysexit, path as syspath
basedir = ospath.abspath(ospath.join(ospath.dirname(__file__),'..','..'))
syspath.insert(1, basedir)
res = {}
parser = ArgumentParser(prog='erd', description = 'Generate ERD diagram')
parser.add_argument('-c','--config',  help = 'Config unless config.json', default='../config.json')
parsedinput = parser.parse_args()
try:
 with open(ospath.abspath(ospath.join(ospath.dirname(__file__), parsedinput.config))) as f:
  config = load(f)['database']
 database,host,username,password = config['name'],config['host'],config['username'],config['password']
except:
 sysexit(1)
else:
 try:
  import eralchemy
 except ImportError:
  try:
   from pip import main as pipmain
  except:
   from pip._internal import main as pipmain
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
 sysexit(0 if res.get('status') == 'OK' else 1)
